#!/usr/bin/env python

import pickle

hg = []
git = []
divided = open('./divided', 'r')

for line in divided.readlines():
    if line.startswith('3'):
        tokens = line.split(';')
        if tokens[1] == 'hg':
            hg.append(tokens[2].rstrip())
        elif tokens[1] == 'git':
            git.append(tokens[2].rstrip())
        else:
            print 'ERROR: Unknown vcs on line', line

print 'Found', len(hg), 'Mercurial repos'
print 'Found', len(git), 'Git repos'

pickle.dump(hg, open('hg.p', 'wb'))
pickle.dump(git, open('git.p', 'wb'))

