from difflib import SequenceMatcher
import os
import string
import nltk
import xml.etree.ElementTree as ET
import re

tokenizer = nltk.data.load('nltk:tokenizers/punkt/english.pickle')


raw_nps = []
nps = []


def MostFrequentKey (np_merge):
   most_freq_key = ''
   most_freq_count = 0

   for a_np_merge in np_merge:
      if a_np_merge[1] > most_freq_count:
         most_freq_key = a_np_merge[0]
         most_freq_count = a_np_merge[1]

   return most_freq_key

def TotalCount (np_merge):
   total = 0

   for a_np_variation in np_merge:
      total += a_np_variation[1]

   return total

def MostFrequentNumWords (np_merge):
   return len(MostFrequentKey(np_merge).split(' '))


def IsBannedKey(key, more_banned_phrases):
   for a_banned_phrase in more_banned_phrases:
      indivi_words = a_banned_phrase.split(' ')
      keys = key.split(' ')
      for a_indivi_word in indivi_words:
         for a_key in keys:
            if SequenceMatcher(None, a_indivi_word, a_key).ratio () > .8:
               return True

   if key == 'product':
      return True
   elif key == 'products':
      return True
   elif key == 'item':
      return True
   elif key == 'items':
      return True
   elif key == 'thing':
      return True
   elif key == 'things':
      return True
   elif key == 'something':
      return True

   return False

def traverse(t):
   try:
      t.node
   except AttributeError:
      return
   else:
      if t.node=='NP': raw_nps.append(t)
      else:
         for child in t:
            traverse(child)


def FindNounPhrases (rawtext, banned):
   sentences = nltk.sent_tokenize(rawtext)

   sentences = [nltk.word_tokenize(sent) for sent in sentences]

   sentences = [nltk.pos_tag(sent) for sent in sentences]

   patterns = """
                  NP: {<NN>*<NNS>}
                      {<NNS>*<NN>}
                      {<JJ>*<NNS>}
                      {<JJ>*<NN>}
                      {<NN>+}
                      {<NNS>+}
   """

   cp = nltk.RegexpParser(patterns)

   trees = [cp.parse(sent) for sent in sentences]

   for t in trees:
      traverse(t)


   merge_nps = []


   for np in raw_nps:
      noun_phrase = ''
      for leaf in np.leaves():
         noun_phrase += leaf[0] + ' '

      nps.append(noun_phrase.strip())


   for np in nps:
      if IsBannedKey (np, banned):
         continue
      finished = False
      for a_merge_np in merge_nps:
         for np_poss in a_merge_np:
            if np_poss[0] == np:
               np_poss[1] += 1
               finished = True
               break
         if finished:
            continue
         if not finished:
            for np_poss in a_merge_np:
               if SequenceMatcher(None, np_poss[0], np).ratio() > .8:
                  #if np_poss[0][0] != np[0] and np_poss[0] in dictionary and np in dictionary:
                  if np_poss[0][0] != np[0]:
                     continue
                  a_merge_np.append ([np,1])
                  finished = True
                  break
      if not finished:
         merge_nps.append([[np,1]])

   mult_frequent_merge_nps = [[],[],[],[],[],[],[],[]]
   for a_merge_np in merge_nps:
      if len(a_merge_np) > 0 and MostFrequentNumWords(a_merge_np) == 1:
         continue
      for j in range(0,len(mult_frequent_merge_nps)):
         if TotalCount(a_merge_np) > TotalCount(mult_frequent_merge_nps[j]):
            for k in reversed(range(j+1, len(mult_frequent_merge_nps))):
               mult_frequent_merge_nps[k] = mult_frequent_merge_nps[k-1]
            mult_frequent_merge_nps[j] = a_merge_np
            break

   single_frequent_merge_nps = [[],[],[],[],[],[],[],[]]

   for a_merge_np in merge_nps:
      if len(a_merge_np) > 0 and MostFrequentNumWords(a_merge_np) > 1:
         continue
      for j in range(0,len(single_frequent_merge_nps)):
         if TotalCount(a_merge_np) > TotalCount(single_frequent_merge_nps[j]):
            for k in reversed(range(j+1, len(single_frequent_merge_nps))):
               single_frequent_merge_nps[k] = single_frequent_merge_nps[k-1]
            single_frequent_merge_nps[j] = a_merge_np
            break

   final_np_list = []

   for single_merge_np in single_frequent_merge_nps:
      in_mult = False
      for i in range(0,len(mult_frequent_merge_nps)):
         matched = False
         for a_single_np in single_merge_np:
            for a_mult_np in mult_frequent_merge_nps[i]:
               words = a_mult_np[0].split(' ')

               for a_word in words:
                  if a_single_np[0] == a_word:
                     in_mult = True
                     for another_a_single_np in single_merge_np:
                        mult_frequent_merge_nps[i].append([another_a_single_np[0],0])
                     matched = True
                     break
               if matched:
                  break
            if matched:
               break

      if not in_mult:
         final_np_list.append(single_merge_np)

   for mult_merge_np in mult_frequent_merge_nps:
      final_np_list.append(mult_merge_np)


   return final_np_list



def ProcessProduct (f, a_product, review_txt):
   global raw_nps
   global nps
   
   f.write ('<product>\n')
   f.write ('<url>\n' + a_product.find('url').text + '\n</url>\n')
   f.write ('<title>\n' + a_product.find('title').text + '\n</title>\n')
   f.write ('<keywords>\n' + a_product.find('keywords').text + '\n</keywords>\n')
   f.write ('<image>\n' + a_product.find('image').text + '\n</image>\n')
   f.write ('<stars>\n' + a_product.find('stars').text + '\n</stars>\n')
   f.write ('<product_name>\n' + a_product.find('product_name').text + '\n</product_name>\n')
   f.write ('<product_code>\n' + a_product.find('product_code').text + '\n</product_code>\n')

   raw_keywords = a_product.find('keywords').text.lower()
   banned_words = []

   for keyword_phrase in raw_keywords.split(','):
      for a_keyword in keyword_phrase.split(' '):
         banned_words.append(a_keyword)      

   np_list = FindNounPhrases(review_txt, banned_words)

   for np_iterations in np_list:
      f.write('<feature>\n')
      for a_np in np_iterations:
         f.write('<sub_feature>\n')
         f.write('<term>' + a_np[0] + '</term>')
	 for a_single_review in a_product.findall('single_review'):
	    if a_np[0] in a_single_review.find('text').text.lower():
               f.write('<single_review>\n')
               f.write('<url>' + a_single_review.find('url').text + '</url>\n')
	       f.write('<text>' + a_single_review.find('text').text + '</text>\n')
               f.write('</single_review>')
         f.write('\n</sub_feature>')
      f.write('\n</feature>')

   f.write ('\n</product>')

   raw_nps = []   
   nps = []
   

def Process (path, file_name):
   f = open (path + '/' + 'processed_' + file_name, 'w')
   f.write('<?xml version="1.0"?>\n<category>\n')

   f_xml = open (path + '/' + file_name, 'r')
   xml = f_xml.read()
   f_xml.close()

   xml = re.sub ('&(?!amp;)', '&amp;', xml).replace('&eacute;','e')

   try:
      root = ET.fromstring(filter(lambda x: x in string.printable, xml).encode("utf8"))
   except Exception as exc:
      return
   
   processed_products = 0

   for a_product in root.findall('product'):
      review_cnt = 0
      review_txt = ''
      for a_single_review in a_product.findall('single_review'):
         review_cnt +=  1
         review_txt += a_single_review.find('text').text.lower()
         if review_cnt > 50:
            break     
 
      if review_cnt > 3:
         ProcessProduct (f, a_product, review_txt)
         processed_products += 1

      if processed_products > 10:
         break

   f.write('\n</category>')
   f.close()
         

def TraverseDirectories (path):
   saw_res = False
   saw_pro = False
   for poss_dir in os.listdir(path):
      if os.path.isdir(path + '/' + poss_dir):
         print ('here 1 ' + path + ' ' + poss_dir)
         TraverseDirectories (path + '/' + poss_dir)
      elif poss_dir == 'results.xml':
         saw_res = True
      elif poss_dir == 'processed_results.xml':
         saw_pro = True
   if saw_res and not saw_pro:  
      print (path) 
      Process(path, 'results.xml')


base_path = '/home/ubuntu/content_farm/nltk_prac/data'

TraverseDirectories (base_path)
