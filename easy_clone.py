#!/usr/bin/env python

#Just keeping things simple

import time, subprocess, os, pickle, threading

CLONEHOME = '/home/ubuntu/clones'
BITBUCKET = 'https://bitbucket.org/'

hg = []
git = []
hg_time = 0
git_time = 0

#This is a generic function that can do the work of either
#Git or Mercurial, depending on what is passed to it
def clone(vcs):
    #Specify that we want to use these global variables
    global hg
    global git
    total_time = 0
    
    #Get the current time
    begin = time.time()

    #Figure out which list we should look through
    if vcs == 'hg':
        my_list = hg
    else:
        my_list = git

    #Go through every repo in our list and try to clone it
    for i in range(len(my_list)):
        #Extract the username and reponame from the full name
        user, repo = my_list[i].split('/')
        #Make a directory for this user. Usernames are unique, so this way,
        #we can keep all of one user's repos in one place safely
        try:
            os.mkdir(CLONEHOME+'/'+vcs+'/'+user)
        except OSError:
            #os.mkdir throws this error if the directory already exists
            #But we don't care, so just print something
            print user+' already had folder'
        #Go into the folder we just made
        os.chdir(CLONEHOME+'/'+vcs+'/'+user)

        #Clone! Syntax for each is a bit different
        if vcs == 'hg':
            subprocess.call(['hg', 'clone', '-U', BITBUCKET+my_list[i]])
        else:
            subprocess.call(['git', 'clone', '--mirror', BITBUCKET+my_list[i]])
        
        #Check our remaining space. This just calls the shell command 'df'
        #and does some splitting to get the number we want
        space = int(subprocess.check_output(['df', '-k', CLONEHOME+'/'+vcs]).split('\n')[1].split()[3])
        #The space is reported in 1KB blocks, so 10,000,000 * 1K = 10GB
        #Each of our VCS folders are on separate drives
        #Over-cautionary limit to space left
        if space < 10000000:
            #"pause" our timer and add the elapsed time to our total timer
            pause = time.time()
            total_time += pause - begin
            #os.system is generally not recommended, but rsync didn't work with subprocess
            os.system('rsync --remove-source-files -ae "ssh -p 2200" '+CLONEHOME+'/'+vcs+' ahota@da2.eecs.utk.edu:')
            #The --remove-source-files flag above deletes files but not the directory structure
            #So we do that separately
            os.system('rm -r '+CLONEHOME+'/'+vcs+'/*')
            #Get the current time again and continue
            begin = time.time()
    
    #Get the final time and find out how long we took
    stop = time.time()
    total_time += stop - begin
    print 'Time taken ('+vcs+'):', total_time
    if vcs == 'hg':
        hg_time = total_time
    else:
        git_time = total_time


#Load our list of repos for Git and Mercurial
hg = pickle.load(open('hg.p', 'rb'))
git = pickle.load(open('git.p', 'rb'))

#Make two threads, one for each VCS
#We target the clone function above and tell it which VCS it is
hg_thread = threading.Thread(target=clone, name='hg_thread', args=('hg',))
git_thread = threading.Thread(target=clone, name='git_thread', args=('git',))

#Let the threads run
hg_thread.start()
git_thread.start()

#Shut down the threads once they exit
hg_thread.join()
git_thread.join()

print 'Git:', git_time
print 'Mercurial:', hg_time
