import json
import os
import re
import string
import xml.etree.ElementTree as ET

overview = []


def Process(path):
   f = open(path, 'r')
   xml = f.read()
   f.close()
   xml = re.sub ('&(?!amp;)', '&amp;', xml).replace('&eacute;','e')

   root = None

   try:
      root = ET.fromstring(filter(lambda x: x in string.printable, xml).encode("utf8"))
   except Exception as exc:
      return

   for a_product in root.findall('product'):
      individual_file = '{'
      page_url = a_product.find('url').text.replace('\n','')
      image_url = a_product.find('image').text.replace('\n','')
      product_code = a_product.find('product_code').text.replace('\n','')
      page_title = a_product.find('product_name').text.replace('-',' ').replace('\n','')
      overview.append({'image_url' : image_url, 'page_title' : page_title, 'product_code' : product_code})
      individual_file = {'page_url': page_url, 'image_url' : image_url, 'page_title' : page_title, 'product_code' : product_code}
      features = [] 
      for a_feature in a_product.findall('feature'):
         a_sub_feature = a_feature.find('sub_feature')
         if a_sub_feature != None:
	    a_term = a_sub_feature.find('term')
	    a_term_txt = ''
	    if a_term != None:
	       a_term_txt = a_term.text.replace('\n','')
               feature_text = []
               for a_sub_feature_2 in a_feature.findall('sub_feature'):
                  for a_single_review in a_sub_feature_2.findall('single_review'):
                     for a_text in a_single_review.findall('text'):
                        feature_text.append(a_text.text.replace('\n',''))
               if len(feature_text) > 0:
                  features.append({'feature_name' : a_term_txt, 'feature_accordion_id' : a_term_txt.replace(' ', ''), 'feature_text' : feature_text, 'feature_curr_text' : feature_text[0], 'feature_curr_text_index': 0})

      individual_file['features'] = features
   
      f = open ('/home/ubuntu/content_farm/igniipotent/reviews/angular-reviews/app/json/' + product_code + '.json', 'w')
      f.write(json.dumps(individual_file))
      f.close()

def TraverseDirectories (base_path, new_path):
   for poss_dir in os.listdir(base_path + '/' + new_path):
      if os.path.isdir(base_path + new_path + '/' + poss_dir):
	 TraverseDirectories (base_path, new_path + '/' + poss_dir)
      elif poss_dir == 'processed_results.xml':
         print (base_path + new_path)
	 Process(base_path + new_path + '/' + poss_dir)

TraverseDirectories('/home/ubuntu/content_farm/nltk_prac/data','')

 
