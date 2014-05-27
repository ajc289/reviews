import string
from bs4 import BeautifulSoup
import re
import urllib2
import os
from threading import Thread,Lock
from time import sleep

at_child = 0
pg_count = 0
leaf_count = 0
leaf_count_lock = Lock()

def ProcessURL (cur_path, a_url):
   global at_child
   global leaf_count

   if leaf_count > 5000:
      return 

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
      return
   left_nav = soup.find(id="leftNavContainer")
  
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
         continue      
      if saw_strong:
         anchor = a_list_item.find('a')
         href = anchor['href']
         if 'http:' in href:
            new_urls.append(href)
         else:
            new_urls.append('http://www.amazon.com' + href)
   
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
      ProcessURL(new_path, a_new_url)

   if len(new_urls) == 0:
      at_child += 1
      f_leaf_html = open (new_path + '/leaf_html.html','w')
      f_leaf_html.write(html)
      f_leaf_html.close()
      with leaf_count_lock:
         leaf_count += 1

urls = [a_url.strip() for a_url in open('/home/ubuntu/content_farm/nltk_prac/urls.txt')]

threads = []

for a_url in urls:
   thread = Thread(target=ProcessURL, args=('/home/ubuntu/content_farm/nltk_prac/data', a_url))
   thread.start()
   threads.append(thread)

for a_thread in threads:
   a_thread.join()
