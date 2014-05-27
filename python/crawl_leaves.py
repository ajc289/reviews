import string
from bs4 import BeautifulSoup
import re
import urllib2
import os
#from multiprocessing import Process,Lock
from threading import Thread,Lock
from time import sleep

limit = 0
at_child = 0
pg_count = 0

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

   while counter < 15:
      new_url = 'http://www.amazon.com/' + product_name + '/product-reviews/' + product_code + '?pageNumber=' + str(counter)
      shld_continue = True
      try:
         html = urllib2.urlopen(new_url, timeout=10).read()
      except Exception as exc:
         print(type(exc))
         shld_continue = False
         pass
        
      if not shld_continue:
         counter += 1
         continue

      new_html = new_html.replace('\n','')
      
      soup = BeautifulSoup (html,'html5lib')

      reviews = soup.findAll('div', {'class', 'reviewText'})
      print (new_url)


      if len(reviews) == 0:
         break

      div_regex = '<div class="reviewText">(.*)</div>'
      m = []

      for a_review in reviews:
         review_text_list = re.findall(div_regex,str(a_review))
         if len(review_text_list) == 0:
            continue
         m.append(review_text_list[0])
 
      if len(m) == 0:
         break

      for i in range(0,len(m)):
	  if 'flashPlayer' in m[i]:
	      m[i] = ''
	  if 'script type="text/javascript"' in m[i]:
	      m[i] = ''

      print ("SIZE " + str(len(m)))
	       
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

   f_xml = open(cur_path + '/results.xml','w')
   f_xml.write('<?xml version="1.0"?>\n<category>\n')

   f_xml_lock = Lock()
   num_processes = 0

   pg_limit = 5
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
            html = urllib2.urlopen(new_url, timeout=10).read()
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
            html = urllib2.urlopen(new_url, timeout=10).read()
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
      next_a = soup.find('a',{'title':'Next page', 'id':'pagnNextLink'})

      if next_a == None:
	 break

      num_pg += 1

      if num_pg > pg_limit:
         break

      new_url = next_a['href']

      html = ''
      try:
         html = urllib2.urlopen(new_url, timeout=10).read()
      except Exception as exc:
         print(type(exc))
         pass
 
      soup = BeautifulSoup (html,'html5lib')

   while len(threads) > 0:
      threads.pop(0).join()

   f_xml.write('</category>\n')
   f_xml.close()


def TraverseDirectories (path):
   print(path)
   global limit
   for poss_dir in os.listdir(path):
      if os.path.isdir(path + '/' + poss_dir):
         TraverseDirectories (path + '/' + poss_dir)
      elif poss_dir == 'leaf_html.html':
         saw_results = False
         for poss_dir in os.listdir(path):
            if poss_dir == 'results.xml':
               saw_results = True
         if saw_results == False:
            f_leaf_html = open(path + '/leaf_html.html', 'r')
            html = f_leaf_html.read()
            f_leaf_html.close()
            soup = BeautifulSoup (html, 'html5lib')
            ProcessLeaf_iter(path, soup)

base_path = '/home/ubuntu/content_farm/nltk_prac/data'

TraverseDirectories (base_path)


