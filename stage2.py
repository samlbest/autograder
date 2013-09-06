__author__ = 'sd'
#  Preliminary version - Untested
#  Runs make in specified directory (or curerent working dir as default)

import subprocess
import os

def run_make(dir=''):
    # Executes the make command in the current directory
    # Runs in the current directory unless the 'dir' parameter is specified
    #  Returns True if make succeeds, False otherwise

    # cmd = 'make'
    if (dir and os.path.exists(dir)) or not dir:

        cmd = ['make'] if not dir else (['make', '-C', dir])

        try:
            #print(cmd)
            make_results = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = make_results.communicate()
            if err:
                return (False, err)
            return (True, out)
        except OSError as o:
            return (False, o.output)
       # except subprocess.TimeoutExpired as e:
       #     log_results('Timeout expired while executing make')

    elif (dir and not os.path.exists(dir)):
        return (False, 'Directory %s does not exist' %dir)
    return (False, "")

if __name__ == '__main__':
    print(run_make())
    print(run_make(dir='~/somedir/dir2'))
    print(run_make(dir = '/home/sd/CS362/cs362s2013/dunbarst/tri-tester'))

