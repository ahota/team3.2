#!/usr/bin/env python

#As a matter of pride, I am making this more robust

import time, subprocess, os, pickle, threading, Queue

CLONEHOME = '/home/ubuntu/test_clones'  #Base directory -> /home/ubuntu/clones/<vcs>/<user>/<repo>
BITBUCKET = 'https://bitbucket.org/'    #Base URL -> https//bitbucket.org/<user>/<repo>
THRESHOLD = 22000000                    #Largest repo is 22GB, need to keep this minimum free space in case it gets cloned
C_THREADS = 30                          #Total number of clone threads -> 15 for each VCS

hg = Queue.Queue()
git = Queue.Queue()
hg_time = 0
git_time = 0
hg_rsync_queue = Queue.Queue()
git_rsync_queue = Queue.Queue()

#Get free disk space at a mount point
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
            command = 'hg clone -U -q '+BITBUCKET+full_name
        else:
            command = 'git clone --mirror --quiet '+BITBUCKET+full_name
        #Piping /dev/null into stdin just in case a repo asks for a username and password
        clone = subprocess.Popen(command, shell=True, stdin=open('/dev/null', 'r'))
        #Call and wait for the clone process to finish
        clone.wait()

        #Add the user whose repo we just cloned to the rsync queue
        #We rsync the user's folder. Since most users only have a few repos, this shouldn't
        #take long
        my_rsync_queue.put(user, block=True)
    
    #Get the final time and find out how long we took
    stop = time.time()
    total_time += stop - start
    print 'Time taken ('+vcs+'):', total_time
    if vcs == 'hg':
        hg_time += total_time
    else:
        git_time += total_time

def rsync(vcs):
    user = my_queue.get(block=True)
    rsync_src = CLONEHOME+'/'+vcs+'/'user
    rsync_dest = '~/'+vcs

    #The threads should use different VMs
    #This is really lazy, but cool
    port = str(2200 + len(vcs))

    #Go to the appropriate folder and rsync the repo
    command = 'rsync --remove-source-files -ae "ssh -p '+port+'" '+rsync_src+' ahota@da2.eecs.utk.edu:'+rsync_dest
    p = subprocess.Popen(command, shell=True, stdin='\n')
    p.wait()
    

#Get the overall start time
begin = time.time()

#Load our queues with the pickled lists of repos for Git and Mercurial
map(hg.put, pickle.load(open('hg.p', 'rb')))
map(git.put, pickle.load(open('git.p', 'rb')))

#Make our cloning threads
#We target the clone function above, so each one runs that function in parallel
hg_threads = []
git_threads = []
for i in range(C_THREADS/2):
    hg_threads.append( threading.Thread(target=clone, name='hg_thread_'+str(i), args=('hg',)) )
    git_threads.append( threading.Thread(target=clone, name='git_thread_'+str(i), args=('git',)) )

#Make our rsync threads
#Targeting the rsync function above
hg_rsync_thread = threading.Thread(target=rsync, name='hg_rsync_thread', args=('hg',))
git_rsync_thread = threading.Thread(target=rsync, name='git_rsync_thread', args=('git',))

#Let the threads run
hg_rsync_thread.start()
git_rsync_thread.start()
for i in range(C_THREADS/2):
    hg_threads[i].start()
    git_threads[i].start()

#Shut down the threads once they exit
for i in range(C_THREADS/2):
    hg_threads[i].join()
    git_threads[i].join()
hg_rsync_thread.join()
git_rsync_thread.join()

end = time.time()

print '-----Clone threads total CPU time-----'
print 'Git:', git_time, 'seconds'
print 'Mercurial:', hg_time, 'seconds'
print '-----Script total execution time-----'
print end - begin, 'seconds'
