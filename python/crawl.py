import string
from bs4 import BeautifulSoup
import re
import urllib2
import os
#from multiprocessing import Process,Lock
from threading import Thread,Lock
from time import sleep

at_child = 0
pg_count = 0
leaf_count = 0
leaf_count_lock = Lock()

def SubRegex (regex, possible_review):
   m = re.findall(regex, possible_review)
    
   if len(m) == 0:
      return possible_review
   else:
      return SubRegex(regex, m[0])

def ProcessProductPage (f_xml_lock, f_xml, a_url, html):
   if a_url[len(a_url)-1] != '/':
      a_url += '/'
   regex = 'com\/(.*?)\/dp\/(.*?)\/'
   m = re.findall(regex, a_url)

   counter = 1
   product_name = m[0][0]
   product_code = m[0][1]
    
   new_html = ''

   regex = '<meta name="title" content="(.*?)" />'
   m = re.findall(regex, html)
   if len(m) == 0:
      return
   title = m[0]

   regex = '<meta name="keywords" content="(.*?)" />'
   m = re.findall(regex, html)
   if len(m) == 0:
      return
   keywords = m[0]

   regex = '<span class="reviewCountTextLinkedHistogram" title="(.*?) out of 5 stars">'
   m = re.findall(regex, html)
   if len(m) == 0:
      return
   stars = m[0]

   regex = 'colorImages\': { \'initial\': \[{"hiRes":"(.*?)","thumb":"http'
   if len(m) == 0:
      return
   m = re.findall(regex, html)
    
   if len(m) == 0:
       regex = '","large":"(.*?)","main":{"'
       m = re.findall(regex, html)
    
   if len(m) == 0:
      return
   
   image_url = m[0]

   xml_result = ''

   #xml_result += '<product>\n'
   #xml_result += '<url>\n' + a_url + '\n</url>\n'
   #xml_result += '<title>\n' + title + '\n</title>\n'
   #xml_result += '<keywords>\n' + keywords + '\n</keywords>\n'
   #xml_result += '<image>\n' + image_url + '\n</image>\n'
   #xml_result += '<stars>\n' + stars + '\n</stars>\n'

   a_url = filter(lambda x: x in string.printable, a_url).encode("utf8")
   title = filter(lambda x: x in string.printable, keywords).encode("utf8")
   image_url = filter(lambda x: x in string.printable, image_url).encode("utf8")
   stars = filter(lambda x: x in string.printable, stars).encode("utf8")
   product_name = filter(lambda x: x in string.printable, product_name).encode("utf8")
   product_code = filter(lambda x: x in string.printable, product_code).encode("utf8")

   xml_result += '<product>\n'
   xml_result += '<url>\n' + a_url + '\n</url>\n'
   xml_result += '<title>\n' + title + '\n</title>\n'
   xml_result += '<keywords>\n' + keywords + '\n</keywords>\n'
   xml_result += '<image>\n' + image_url + '\n</image>\n'
   xml_result += '<stars>\n' + stars + '\n</stars>\n'
   xml_result += '<product_name>\n' + product_name + '\n</product_name>\n'
   xml_result += '<product_code>\n' + product_code + '\n</product_code>\n'

   while 1==1:
      new_url = 'http://www.amazon.com/' + product_name + '/product-reviews/' + product_code + '?pageNumber=' + str(counter)
        
      new_html = urllib2.urlopen(new_url).read()
      new_html = new_html.replace('\n','')
       
      regex = '<\/b>\s+<\/div>(.*?)<div style="padding-top: 10px; clear: both; width: 100%;">'
      m = re.findall(regex, new_html)
       
      if len(m) == 0:
	  break
       
      for i in range(0, len(m)):
	  m[i] = SubRegex('<br \/><\/span>\s+<\/div>(.*)',SubRegex('<\/div>\s+<\/div>(.*)',SubRegex('<\/span>\s+<\/div>(.*)', SubRegex('<\/b>\s+<\/div>(.*)', m[i]))))

      for i in range(0,len(m)):
	  if 'flashPlayer' in m[i]:
	      m[i] = ''
	  if 'script type="text/javascript"' in m[i]:
	      m[i] = ''
	       
      for i in range(0,len(m)):
	  m[i] = m[i].replace('<\/b>', '').replace('<b \/>', '')
	  m[i] = re.sub(r'<.*?>', '', m[i])
   
          new_url = filter(lambda x: x in string.printable, new_url).encode("utf8")
          m[i] = filter(lambda x: x in string.printable, m[i]).encode("utf8")
	 
          xml_result += '<single_review>\n' 
          xml_result += '<url>\n' + new_url + '\n</url>\n'
	  xml_result += '<text>\n' + m[i] + '\n</text>\n'
          xml_result += '\n</single_review>'

      counter += 1
  
   f_xml.write(xml_result + '</product>\n')

def ProcessLeaf (soup):
   divs = soup.findAll('div',{'class':'productTitle'})

   try:
      for a_div in divs:
	 a_anchor = a_div.find('a')
	 new_url = a_anchor['href']
	 html = urllib2.urlopen(new_url).read()
	 #ProcessProductPage (new_url,html)
      global pg_count
      pg_count += 1
      print(pg_count)
      next_a = soup.find('a',{'title':'Next page', 'id':'pagnNextLink'})

      if next_a == None:
	 return
      
      new_url = next_a['href']
      print(new_url)
      html = urllib2.urlopen(new_url).read()
      soup = BeautifulSoup (html,'html5lib')
   except:
      print ('caught exception')
      pass

   ProcessLeaf(soup)


def ProcessLeaf_iter (cur_path, soup):
   threads = []
   f_shit = open(cur_path + '/shit.html','w')
   f_shit.write(str(soup))
   f_shit.close()

   f_xml = open(cur_path + '/results.xml','w')
   f_xml.write('<?xml version="1.0"?>\n<category>\n')

   f_xml_lock = Lock()
   num_processes = 0

   pg_limit = 7
   num_pg = 0

   while 1==1:
      headers = soup.findAll('h3', {'class', 'newaps'})

      for a_header in headers:
         if a_header == None:
            continue
         link = a_header.findNext('a')
         if link == None:
            continue

         new_url = link['href']

         html = ''
         shld_continue = False
          
         try:
            html = urllib2.urlopen(new_url).read()
         except Exception as exc:
            shld_continue = True
            print(type(exc))
            pass

         if shld_continue:
            continue

	 thread = Thread(target=ProcessProductPage, args=(f_xml_lock, f_xml,new_url,html))
         thread.start()
         threads.append(thread)

      divs = soup.findAll('div',{'class':'productTitle'})

      for a_div in divs:
         if a_div == None:
            continue
         a_anchor = a_div.find('a')
         if a_anchor == None:
            continue

         new_url = a_anchor['href']

         html = ''
         shld_continue = False

         try:
            html = urllib2.urlopen(new_url).read()
         except Exception as exc:
            shld_continue = True
            print(type(exc))
            pass

         if shld_continue:
            continue

         thread = Thread(target=ProcessProductPage, args=(f_xml_lock, f_xml,new_url,html))
         thread.start()
         threads.append(thread)

      global pg_count
      pg_count += 1
      print(pg_count)
      next_a = soup.find('a',{'title':'Next page', 'id':'pagnNextLink'})

      if next_a == None:
	 break

      num_pg += 1

      if num_pg > pg_limit:
         break

      new_url = next_a['href']
      print(new_url)

      html = ''
      try:
         html = urllib2.urlopen(new_url).read()
      except Exception as exc:
         print(type(exc))
         pass
 
      soup = BeautifulSoup (html,'html5lib')

   while len(threads) > 0:
      threads.pop(0).join()

   f_xml.write('</category>\n')
   f_xml.close()

def ProcessURL (cur_path, a_url):
   global at_child
   global leaf_count

   if leaf_count > 5000:
      return 

   #a_url = 'http://www.amazon.com/s?rh=n%3A289680'
   #a_url = 'http://www.amazon.com/s?ie=UTF8&page=44&rh=n%3A289680'
   html = ''
   
   shld_exit = False

   try:
      html = urllib2.urlopen(a_url, timeout=10).read()
   except Exception as exc:
      print (type(exc))
      shld_exit = True
      pass

   if shld_exit:
      return
   
   soup = BeautifulSoup (html,'html5lib')
   if soup.body == None:
      print('fuck')
      return
   left_nav = soup.find(id="leftNavContainer")
  
   #unordered_list = left_nav.find('ul')
   unordered_list = None
   dept_headers = left_nav.find_all('h2')
   for a_header in dept_headers:
      if a_header.text == 'Department':
         unordered_list = a_header.findNext('ul')
         break
  
   if unordered_list == None:
      return
 
   saw_strong = False
   new_urls = []
   cur_name = ''

   for a_list_item in unordered_list.find_all('li'):
      if not saw_strong  and a_list_item.find('strong') != None:
         saw_strong = True
         cur_name = a_list_item.find('strong').contents
         #print(cur_name)
         continue      
      if saw_strong:
         anchor = a_list_item.find('a')
         href = anchor['href']
         if 'http:' in href:
            new_urls.append(href)
         else:
            new_urls.append('http://www.amazon.com' + href)
         #name = a_list_item.find('span').contents
   
   no_space_cur_name = cur_name[0].replace(' ', '_')
   no_space_cur_name = no_space_cur_name.replace('&','')
   no_space_cur_name = no_space_cur_name.replace('\'','')
   no_space_cur_name = no_space_cur_name.replace('"','')
   no_space_cur_name = no_space_cur_name.replace(',','')
   no_space_cur_name = filter(lambda x: x in string.printable, no_space_cur_name).encode("utf8")

   print('cur_name ' + no_space_cur_name)     
   new_path = cur_path + '/' + no_space_cur_name

   print('new_path ' + new_path)

   os.system('mkdir ' + new_path)

   for a_new_url in new_urls:
      #if at_child == 1:
         #break
      ProcessURL(new_path, a_new_url)

   if len(new_urls) == 0:
      at_child += 1
      f_leaf_html = open (new_path + '/leaf_html.html','w')
      f_leaf_html.write(html)
      f_leaf_html.close()
      with leaf_count_lock:
         leaf_count += 1
      #ProcessLeaf_iter(new_path, soup)

urls = [a_url.strip() for a_url in open('/home/ubuntu/content_farm/nltk_prac/urls.txt')]
#urls = [a_url.strip() for a_url in open('/home/ubuntu/content_farm/nltk_prac/urls_4.txt')]

threads = []

for a_url in urls:
   #ProcessURL ('/home/ubuntu/content_farm/nltk_prac/data', a_url)
   thread = Thread(target=ProcessURL, args=('/home/ubuntu/content_farm/nltk_prac/data', a_url))
   thread.start()
   threads.append(thread)

for a_thread in threads:
   a_thread.join()
