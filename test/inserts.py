#!/usr/bin/python

# The structure of each record is assumed to be as follows: 
#
# commit: 7385492a3745b89734c259873d32859e03f224342434
# Author: Amirouche Boubekki <amirouche.boubekki@gmail.com>
# Date: Sat Sept 13 12:40:52 2014 +200
# Here is the commit message.
#
# A line break separates each quartet of lines. 
# We are going to take each quartet and put it into an object like the one immediately below. 
#

record = { 'commit': { 'hash': '', 'author': '', 'email': '', 'date': '', 'message': '' } }

with open('ajgu-graphdb_git.log', 'r') as f: 
  for line in f:

    lineLen = len(line.split())
    i = 1
    if lineLen > 0: 
      
      if line.split()[0] == 'commit':
        record['commit']['hash'] = line.split()[1]

      elif line.split()[0] == 'Author:':
        emailFlag = False
        record['commit']['author'] = ''
        record['commit']['email'] = ''
        while i < lineLen: 
          if emailFlag == False: 
            record['commit']['author'] += line.split()[i] + ' '
            if line.split()[i+1][0] == '<': 
              emailFlag = True
          else:
            record['commit']['email'] += line.split()[i] + ' '
          i = i + 1
        record['commit']['author'] = record['commit']['author'].rstrip()
        record['commit']['email'] = record['commit']['email'].rstrip()

      elif line.split()[0] == 'Date:':
        record['commit']['date'] = ''
        while i < lineLen: 
          record['commit']['date'] += line.split()[i] + ' '
          i = i + 1
        record['commit']['date'] = record['commit']['date'].rstrip()

      # This block captures the commit message. 
      else: 
        record['commit']['message'] = ''
        while i < lineLen: 
          record['commit']['message'] += line.split()[i] + ' '
          i = i + 1
        record['commit']['message'] = record['commit']['message'].rstrip()
        print(record)


# Once the record is built, insert it into the database.

f.close()


