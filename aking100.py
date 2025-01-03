import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'aking100'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = '/blob/master/README.md' # or it could be 'blob/main/README.md'
postGHMain = '/blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

BIBpattern: str = r'@\w+\{[^}]+\}'

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

def extractBIBs (c):
  res = re.findall (BIBpattern, c, re.DOTALL)
  return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
 post0 = post
 with open(f"input/{utid}_{tp}.txt", 'r') as f:
  for line in f:
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';');
    post0 = postGH
   print(line)
   url = base[tp] + f"{line}{post0}"
   r = requests.get (url)
   # Check upon error
   if r.status_code == 404:
      # Continue on Error
      if tp != 'source':
         continue
      # If error on GH, try main instead of master
      url = base[tp] + f"{line}{postGHMain}"
      r = requests.get(url)
      # Actual error, skip
      if r.status_code == 404:
         continue
      # Just master vs. main error, continue on
   content = r.text;
   urls = extractURLs(content)
   dois = extractDOIs(content)
   bibs = extractBIBs(content)
   res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())

run('model')
run('data')
run('source')