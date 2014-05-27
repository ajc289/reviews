import json
import os
import socket
import re
import string
import xml.etree.ElementTree as ET

overview = []

inverted_index = {}

class Product:
   def __init__(self, image_url, product_code, page_title, stars):
      self.image_url = image_url
      self.product_code = product_code
      self.page_title = page_title
      self.stars = stars

class Frequency:
   def __init__(self, prod, freq):
      self.prod = prod
      self.freq = freq

def AnswerSearch(search_terms):
   global inverted_index
   search_result = {}
   search_result_list = []
   for term in search_terms:
      if term in inverted_index:
         for a_prod in inverted_index[term]:
            if a_prod.product_code in search_result:
               search_result[a_prod.product_code].freq += 1
            else:
               search_result[a_prod.product_code] = Frequency(a_prod,1)
   
   for a_key in search_result:
      search_result_list.append(search_result[a_key])

   search_result_list.sort(key=lambda x: x.freq)

   for_json = {'result' : []}

   for a_res in search_result_list:
      for_json['result'].append({'image_url': a_res.prod.image_url, 'product_code': a_res.prod.product_code, 'page_title': a_res.prod.page_title, 'stars': a_res.prod.stars})

   return for_json

def PreProcessSearch (orig_search_terms):
   search_terms = []
   for a_term in orig_search_terms.split(';'):
      search_terms.append(a_term.replace('\n','').lower())

   return AnswerSearch(search_terms)

def BuildInvertedIndex(path, sub_directories):
   global inverted_index
   f = open(path, 'r')
   xml = f.read()
   f.close()
   xml = re.sub ('&(?!amp;)', '&amp;', xml).replace('&eacute;','e')

   path_keywords = []

   for term in sub_directories.split('/'):
      for sub_term in term.split('_'):
         path_keywords.append(sub_term)

   root = None

   try:
      root = ET.fromstring(filter(lambda x: x in string.printable, xml).encode("utf8"))
   except Exception as exc:
      return

   for a_product in root.findall('product'):
      image_url = a_product.find('image').text.replace('\n','')
      product_code = a_product.find('product_code').text.replace('\n','')
      page_title = a_product.find('product_name').text.replace('-',' ').replace('\n','')
      keywords = a_product.find('keywords').text.replace('\n','').split(',')
      stars = float(a_product.find('stars').text.replace('\n',''))

      new_product = Product(image_url, product_code, page_title, stars)

      merged_keywords = keywords + path_keywords + page_title.split(' ')

      for a_keyword in merged_keywords:
         if a_keyword.lower() in inverted_index:
            inverted_index[a_keyword.lower()].append(new_product)
         else:
            inverted_index[a_keyword.lower()] = [new_product]
      

def TraverseDirectories (base_path, new_path):
   for poss_dir in os.listdir(base_path + '/' + new_path):
      if os.path.isdir(base_path + new_path + '/' + poss_dir):
	 TraverseDirectories (base_path, new_path + '/' + poss_dir)
      elif poss_dir == 'processed_results.xml':
         #print (base_path + new_path)
	 BuildInvertedIndex(base_path + new_path + '/' + poss_dir, new_path)



TraverseDirectories('/home/ubuntu/content_farm/nltk_prac/data','')

print('done')

ADDR = ("localhost", 9300)

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind(ADDR)
listener.listen(10)

while 1==1:
   server, client_addr = listener.accept()
   print ('got get')
   sf = server.makefile("r+b", bufsize=0)

   res = sf.readlines()

   search_ans = PreProcessSearch(res[0])

   print(json.dumps(search_ans))
   sf.write(json.dumps(search_ans))
   sf.flush()
   sf.close()
   server.close()
   









 
