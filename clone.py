#!/usr/bin/env python

import pickle, threading, subprocess, os, time

err_file = '/home/ubuntu/clones/errors.log'
err_file_lock = threading.Lock()
BITBUCKET_PREFIX = 'https://bitbucket.org/'
HOME_DIR = '/home/ubuntu/clones'
space_lock = threading.Lock()
GIT_DONE = False
HG_DONE = False
THRESHOLD = 73258480

def clone(vcs, repo_list):
    global err_file
    global err_file_lock
    global space_lock
    global GIT_DONE
    global HG_DONE
    if vcs == 'hg':
        os.chdir(HOME_DIR+'/hg')
    else:
        os.chdir(HOME_DIR+'/git')
    for full_name in repo_list:
        while(not space_lock.acquire(False)):
            time.sleep(1)
        space_lock.release()
        user, repo = full_name.split('/')
        try:
            os.mkdir(user)
        except OSError as e:
            pass
        try:
            if vcs == 'hg':
                os.chdir(HOME_DIR+'/hg/'+user)
            else:
                os.chdir(HOME_DIR+'/git/'+user)
        except OSError as e:
            print e
            exit()
        try:
            if vcs == 'hg':
                dolly = subprocess.Popen(['hg', 'clone', '-U', BITBUCKET_PREFIX+full_name])
            else:
                dolly = subprocess.Popen(['git', 'clone', '--mirror', BITBUCKET_PREFIX+full_name])
            dolly.wait()
        except subprocess.CalledProcessError as e:
            with err_file_lock:
                with open(err_file, 'wb') as log:
                    log.write(e+'\n')
        if vcs == 'hg':
            os.chdir(HOME_DIR+'/hg')
        else:
            os.chdir(HOME_DIR+'/git')
    if vcs == 'hg':
        HG_DONE = True
    else:
        GIT_DONE = True

def check_space(vcs):
    global GIT_DONE
    global HG_DONE
    global THRESHOLD
    if vcs == 'hg':
        os.chdir(HOME_DIR+'/hg')
        flag = HG_DONE
    else:
        os.chdir(HOME_DIR+'/git')
        flag = GIT_DONE
    while(not flag):
        space = int(subprocess.check_output(['df', '-k', '.']).split('\n')[1].split()[3])
        if space < THRESHOLD:
            with space_lock:
                if vcs == 'hg':
                    rsync = subprocess.Popen(['rsync', '-ae', '\'ssh -p 2200\'', '--remove-source-files', HOME_DIR+'/hg', 'ahota@da2.eecs.utk.edu:hg'])
                else:
                    rsync = subprocess.Popen(['rsync', '-ae', '\'ssh -p 2200\'', '--remove-source-files', HOME_DIR+'/git', 'ahota@da2.eecs.utk.edu:git'])
                rsync.wait()


try:
    hg_list = pickle.load(open('hg.p', 'rb'))
    git_list = pickle.load(open('git.p', 'rb'))
except IOError as e:
    print e
    print 'Error with pickle files, run get_repos.py'
    exit()

print 'Found', len(hg_list), 'Mercurial repos'
print 'Found', len(git_list), 'Git repos'

hg_thread = threading.Thread(target=clone, name='hg_thread', args=('hg', hg_list))
git_thread = threading.Thread(target=clone, name='git_thread', args=('git', git_list))
hg_space_thread = threading.Thread(target=check_space, name='hg_space_thread', args=('hg',))
git_space_thread = threading.Thread(target=check_space, name='git_space_thread', args=('git',))

hg_thread.start()
git_thread.start()
hg_space_thread.start()
git_space_thread.start()

hg_thread.join()
git_thread.join()
hg_space_thread.join()
git_space_thead.join()

