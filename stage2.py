import subprocess
import os

# Executes the make command in the current directory
# Runs in the current directory unless the 'dir' parameter is specified
def run_make(dir='.'):

    if (dir and os.path.exists(dir)) or not dir:

        cmd = ['make'] if not dir else (['make', '-C', dir])

        try:
            make_results = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = make_results.communicate()
            if err:
                return (False, err)
            return (True, out)
        except OSError as o:
            return (False, o.output)

    elif (dir and not os.path.exists(dir)):
        return (False, 'Directory %s does not exist' %dir)
    return (False, "")
