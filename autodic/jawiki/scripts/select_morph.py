#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals, print_function, division
import sys
import codecs
sys.stdin = codecs.getreader('utf-8')(sys.stdin)

import os
import gzip
import re
import urllib
import mojimoji
import ctypes
import argparse
import textwrap
import unicodedata
import cdb

from collections import defaultdict

dump_base_url = 'https://dumps.wikimedia.org/jawiki/latest/'
dump_files = ('jawiki-latest-page.sql.gz', 'jawiki-latest-redirect.sql.gz')
data_dir = os.path.dirname(os.path.abspath(__file__)) 
output_dir = os.path.dirname(os.path.abspath(__file__)) 

from pyknp import Juman
juman = Juman()

re_parentheses_id2title = re.compile(r"\((\d+),\d+,'?([^,']+)'?,[^\)]+\)")
re_title_brackets = re.compile(r'[ _]\([^\)]+\)$')

re_all_katakana = re.compile(r'^(?:\xE3\x82[\xA1-\xBF]|\xE3\x83[\x80-\xB6])+$')
re_alias = re.compile(r'_\(.*?\)')
re_alldigit = re.compile(r'^[\-\+0-9\.,]+$')
re_somelist = re.compile(r'一覧$')
re_someappearance = re.compile(r'の登場')
re_test_ignore1 = re.compile(r'^[\+\-\.\(\)\?\*\$\!\_\\\'"/&%,]+')
re_test_ignore2 = re.compile(r'[:/]')

IGNORE_PREFIX = ('削除依頼/', '検証/', '進行中の荒らし行為/', '井戸端/', 'WP:',
                 '利用者:', 'ウィキプロジェクト', 'PJ:')
IGNORE_SUBSTR = ('Wikipedia:', 'Template:', 'Listes:', '過去ログ:', 'ファイル:', '画像:',
                 'Section:')

len_threshold = 12
len_threshold_in_specific_category = 20

#import ctypes
#dsim = ctypes.cdll.LoadLibrary('libdsim.so.1')
#dsim.init_dsim(ctypes.c_char_p(data_dir + '/mrph2id.db'))
#similarity = dsim.similarity
#similarity.restype = ctypes.c_float
#similarity.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
#distsim_threshold = 0.2

single_mrph_hyponymy_suffix = ('駅'.encode('utf8'), '学校'.encode('utf8'))

single_mrph_words, multiple_mrph_words = [], []
debug_container = defaultdict(list)

counter = 1
def main(args):
  global data_dir
  data_dir = args['data_dir']
  global output_dir
  output_dir = args['output_dir']

  if args['download']:
    for f in dump_files:
      print('Downloading %s ...' % f)
      url.urlretrieve(os.path.join(dump_base_url, f), os.path.join(data_dir, f))
      print('Download completed')
  
  global hyponymy_db
  hyponymy_db = cdb.init(data_dir + '/hyponymy.cdb'.encode('utf8'))
  redirect_dict = get_redirect_dict()
  try:
    from tqdm import tqdm
    title_pbar = tqdm(extract_titles_from_abstract_xml())
    title_pbar.set_description('Title Progress')
    for title in title_pbar:
      if not title in redirect_dict: 
        process(title, redirect=None)
    
    redirect_pbar = tqdm(redirect_dict.items())
    redirect_pbar.set_description('Redirect Progress')
    for title, redirect in redirect_pbar:
      process(title, redirect)
  finally:
    write(sorted(single_mrph_words), os.path.join(output_dir, 'single_morph.txt'))
    write(sorted(multiple_mrph_words), os.path.join(output_dir, 'multiple_morph.txt'))

    # debug basis
    for k, v in debug_container.items():
      write(sorted(v), os.path.join(output_dir, k))

def process(title, redirect=None):
  global counter
  #if counter % 10000 == 0:
  #  print(counter)
  counter += 1
  
  try:
    if is_garbage_word(title):
      return
        
    ztitle = mojimoji.han_to_zen(title)
    mrphs = juman.analysis(ztitle).mrph_list()
        
    if len(mrphs) == 1 and not mrphs[0].hinsi == '未定義語':
      debug_container['G_juman'].append(title)
    elif is_garbage_mrphs(mrphs):
      debug_container['G_mrph'].append(title)
    elif is_single_mrph(title, ztitle, mrphs) or is_specific_category(title, redirect):
      single_mrph_words.append(title)
    else:
      multiple_mrph_words.append(title)
  except Exception, details:
    sys.stderr.write('Error %s %s %s\n'%(type(title), title, details))

def get_redirect_dict():
  id_redirect = extract_id2title_from_sql(os.path.join(data_dir, 'jawiki-latest-redirect.sql.gz'))
  id_title = extract_id2title_from_sql(os.path.join(data_dir, 'jawiki-latest-page.sql.gz'))
  redirect2title = dict((normalize(id_title[e[0]]), normalize(e[1])) for e in id_redirect.iteritems() if e[0] in id_title)
  del id_redirect
  return redirect2title

def extract_titles_from_abstract_xml():
  re_title = re.compile(r'<title>Wikipedia: (.+?)</title>')
  return [normalize(re_title.search(l).group(1)) for l in sys.stdin]

def extract_id2title_from_sql(path):
  with gzip.GzipFile(path) as fd:
    return dict(re_parentheses_id2title.findall(fd.read().decode('utf8')))

def normalize(title):
  title = re_title_brackets.sub('', title)
  return title.replace('_', ' ')

def is_valid_title(title):
  if title.startswith(IGNORE_PREFIX):
    return False
  return not any(s in title for s in IGNORE_SUBSTR)

def is_garbage_mrphs(mrphs):
  if len(mrphs) == 2 and mrphs[0].hinsi == '接頭辞' and mrphs[1].hinsi == '名詞':
    return True
  else:
    return False

def is_garbage_word(w):
  flag = False
  if len(w) == 1:
    debug_container['G_single'].append(w)
    flag = True
  elif not is_valid_title(w):
    debug_container['G_invalidtitle'].append(w)
    flat = True 
  elif not re_alldigit.search(w) == None:
    debug_container['G_alldigit'].append(w)
    flag = True
  elif len(w) == 2 and unicodedata.name(w[0])[0:8] == "HIRAGANA" and unicodedata.name(w[1])[0:8] == "HIRAGANA":
    debug_container['G_hiragana2'].append(w)
    flag = True
  #elif not re_alias.search(w) == None:
  #  debug_container['G_alias'].append(w)
  #  flag = True
  elif not re_somelist.search(w) == None:
    debug_container['G_somelist'].append(w)
    flag = True
  elif not re_someappearance.search(w) == None:
    debug_container['G_someappearance'].append(w)
    flag = True
  elif not re_test_ignore1.search(w) == None:
    debug_container['G_test_ignore1'].append(w)
    flag = True 
  elif not re_test_ignore2.search(w) == None:
    debug_container['G_test_ignore2'].append(w)
    flag = True 
  else:
    count = 0
    for i, c in enumerate(w):
      if not (unicodedata.name(c)[0:8] == "HIRAGANA" or
              unicodedata.name(c)[0:8] == "KATAKANA" or
              unicodedata.name(c)[0:3] == "CJK" or
              unicodedata.name(c)[0:5] == "DIGIT" or
              unicodedata.name(c)[0:5] == "LATIN" or
              unicodedata.name(c)[0:5] == "SPACE"):
        count += 1
        if count == 2 and i+1 == 2:
          debug_container['G_not_hkcdl_head'].append(w)
          flag = True
          break

    if 8 < len(w) and 3 < count:
      debug_container['G_hkcdl_ratio'].append(w)
      flag = True
  return flag  

def is_single_mrph(t, ztitle, mrphs):
  if len_threshold <= len(t):
    return False
  
  if len(mrphs) == 1 and mrphs[0].hinsi == '未定義語':
    basis = 'F_undefined'
  elif is_singles(mrphs, t):
    basis = 'F_singles'
  elif 1 < len(mrphs) and re_all_katakana.match(ztitle) and is_similar_to_head(mrphs):
    basis = 'F_distsim'
  else:
    basis = None
  
  if basis:
    debug_container[basis].append(t)
    return True
  else:
    return False

def is_specific_category(title, redirect):
  if len_threshold_in_specific_category <= len(title):
    return False
  
  if redirect:
    s = redirect.encode('utf8')
  else:
    s = title.encode('utf8')

  #if hyponymy_db.has_key(s) and re.split('\s', hyponymy_db[s])[0] in single_mrph_hyponymy:
  if hyponymy_db.has_key(s) and any(re.split('\s', hyponymy_db[s])[0].endswith(suffix) for suffix in single_mrph_hyponymy_suffix):
    debug_container['F_category'].append(title)
    return True
  else:
    return False

def is_singles(mrphs, s):
  if any(1 < len(mrph.midasi) for mrph in mrphs):
    return False
  elif all(mrph.bunrui == '地名' for mrph in mrphs):
    debug_container['F_singles_location'].append(s)
    return False
  elif (  all(hinsi in ('名詞', '接頭辞', '接尾辞') for hinsi in (mrph.hinsi for mrph in mrphs))
      and all(bunrui == '数詞' for bunrui in (mrph.bunrui for mrph in mrphs if mrph.hinsi == '名詞'))):
    debug_container['F_singles_pre_num_post'].append(s)
    return False

  if (  len(mrphs) == 3
    and mrphs[0].hinsi == '名詞' and mrphs[1].midasi in ['の', 'と'] and mrphs[2].hinsi == '名詞'):
      debug_container['F_singles_noun_no_noun'].append(s)
      return False

  return True

def is_similart_to_head(mrphs):
  elemzip = zip([(mrph.midasi, mrph.yomi) for mrph in mrphs])
  word = ''.join(z[0]) + '/' + ''.join(z[1])
  head = mrphs[:-1].midasi + '/' + mrphs[:-1].yomi
  print('%s %s'%(main, head))
  score = similarity(word, head)
  return score <= distsim_threshold  

def write(words, path):
  print('Writing %s'%path)
  with codecs.open(path, 'w', 'utf-8') as out:
    for w in words:
      out.write('%s\n'%w)
    out.flush()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description='Wikipedia title classifier for rebuild auto dictionary of Kyoto Parser(JUMAN, KNP)'
  )
  
  parser.add_argument('-l', '--download', action="store_true", default=False,
                        help="Download wikipedia dumps")
  parser.add_argument('-d', '--data-dir', type=str, default='.',
                        help="")
  parser.add_argument('-o', '--output-dir', type=str, default='.',
                        help="")

  main(vars(parser.parse_args()))

