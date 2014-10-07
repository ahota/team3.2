#!/usr/bin/env python

#As a matter of pride, I am making this more robust

import time, subprocess, os, pickle, threading, Queue

CLONEHOME = '/home/ubuntu/test_clones'  #Base directory -> /home/ubuntu/clones/<vcs>/<user>/<repo>
BITBUCKET = 'https://bitbucket.org/'    #Base URL -> https//bitbucket.org/<user>/<repo>
THRESHOLD = 22000000                    #Largest repo is 22GB, need to keep this minimum free space in case it gets cloned
C_THREADS = 28                          #Total number of clone threads -> 14 for each VCS
R_THREADS = 4                           #Total number of rsync threads -> 2 for each VCS

hg = Queue.Queue()
git = Queue.Queue()
hg_time = 0
git_time = 0
hg_rsync_queue = Queue.Queue()
git_rsync_queue= Queue.Queue()

def get_disk_space(mount):
    return int(subprocess.check_output(['df', '-k', mount]).split('\n')[1].split()[3])

#This is a generic function that can do the work of either
#Git or Mercurial, depending on what is passed to it
def clone(vcs):
    
    #Get the current time
    start = time.time()

    #Figure out which list we should look through and which queue to use
    if vcs == 'hg':
        my_queue = hg
        my_rsync_queue = hg_rsync_queue
    else:
        my_queue = git
        my_rsync_queue = git_rsync_queue

    #Go through every repo in the queue and try to clone it
    while not my_queue.empty():
        
        #Check our remaining space. This just calls the shell command 'df'
        #and does some splitting to get the number we want
        #If the space remaining is not enough, sleep until there is
        space = get_disk_space(CLONEHOME+'/'+vcs)
        while(space <= THRESHOLD):
            #This should only happen when rsync threads haven't caught up yet
            #Sleep for 5 seconds so we're not hammering the system with 'df'
            time.sleep(5)
            space = get_disk_space(CLONEHOME+'/'+vcs)

        #Extract the username and reponame from the full name
        full_name = my_queue.get(block=True)
        user, repo = full_name.split('/')
        #Make a directory for this user. Usernames are unique, so this way,
        #we can keep all of one user's repos in one place safely
        try:
            os.mkdir(CLONEHOME+'/'+vcs+'/'+user)
        except OSError:
            #os.mkdir throws this error if the directory already exists
            #But we don't care, so just pass
            pass
        #Go into the folder we just made
        os.chdir(CLONEHOME+'/'+vcs+'/'+user)

        #Clone!
        if vcs == 'hg':
            time.sleep(10)
            #subprocess.call(['hg', 'clone', '-U', '-q', BITBUCKET+my_list[i]])
        else:
            time.sleep(3)
            #subprocess.call(['git', 'clone', '--mirror', '--quiet', BITBUCKET+my_list[i]])

        #Add the repo we just cloned into the rsync queue
        my_rsync_queue.put(full_name, block=True)
    
    #Get the final time and find out how long we took
    stop = time.time()
    total_time += stop - start
    print 'Time taken ('+vcs+'):', total_time
    if vcs == 'hg':
        hg_time = total_time
    else:
        git_time = total_time

def rsync(vcs):
    #Figure out which queue to get repos from
    if vcs == 'hg':
        my_queue = hg_rsync_queue
    else:
        my_queue = git_rsync_queue

    #Get the username and repo name from the queue
    full_name = my_queue.get(block=True)
    user, repo = full_name.split('/')

    #Go to the appropriate folder and rsync the repo
    os.chdir(CLONEHOME+'/'+vcs+'/'+user)
    time.sleep(2)
    #os.system('rsync --remove-source-files -ae "ssh -p 2200" ./'+repo+' ahota@da2.eecs.utk.edu')
    #I'm excluding the rm -rf command because it could potentially delete a repo that didn't successfully rsync




#Load our queues with the pickled lists of repos for Git and Mercurial
map(hg.put, pickle.load(open('hg.p', 'rb')))
map(git.put, pickle.load(open('git.p', 'rb')))

#Make two threads, one for each VCS
#We target the clone function above and tell it which VCS it is
#hg_thread = threading.Thread(target=clone, name='hg_thread', args=('hg',))
#git_thread = threading.Thread(target=clone, name='git_thread', args=('git',))

hg_threads = []
git_threads = []
for i in range(C_THREADS/2):
    hg_threads.append( threading.Thread(target=clone, name='hg_thread_'+str(i), args=('hg',)) )
    git_threads.append( threading.Thread(target=clone, name='git_thread_'+str(i), args=('git',)) )


#Let the threads run
for i in range(C_THREADS/2):
    hg_threads[i].start()
    git_threads[i].start()

#Shut down the threads once they exit
for i in range(C_THREADS/2):
    hg_threads[i].join()
    git_threads[i].join()

print 'Git:', git_time
print 'Mercurial:', hg_time
