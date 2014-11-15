#!/usr/bin/python

# The purpose of this script is to count how many projects users have contributed to, but 
# not counting projects they have started. 

import pymongo, re
from urlparse import urlparse

client = pymongo.MongoClient('da0.eecs.utk.edu')

db = client['test']

commits = db.commits

table = {}

i = 0
for doc in commits.find():
  if doc and doc['committer'] and doc['committer']['login'] and doc['commit'] and doc['commit']['url']:
    # Get the user name.
    user = doc['committer']['login']

    # Get the project name. 
    url = urlparse(doc['commit']['url'])
    m = re.search('/repos/(.*?)/(.*?)/.*', url[2])
    owner = m.group(1)
    project = m.group(2)

    if user not in table: 
      table[user] = [project]
    else: 
      # Check if project is already listed for user.
      addFlag = True
      for proj in table[user]: 
        if proj == project: 
          addFlag = False
        if owner == user: 
          addFlag = False
      if addFlag: 
        table[user].append(project)

    i = i + 1
    if i == 1000000: 
      break

client.close()

for k, v in table.iteritems(): 
  print k + ': ' +str(len(v))
