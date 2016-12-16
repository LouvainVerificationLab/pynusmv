'''
# This script checks that all the system tools and libraries required to proceed
# to the compilation of pynusmv and its native dependencies are installed on your
# machine.
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: X. Gillard <xavier.gillard [at] uclouvain.be>
'''
import os
import os.path
import sys
import platform

# The set of tools required  to proceed to the compilation.
REQUIRED_TOOLS = [
    # Imposed by NuSMV (see NuSMV / README)
    'gcc', 'flex', 'bison', 'make', 'tar', 'gzip', 'unzip',
    # Imposed by MiniSAT
    'g++', 'patch', 'ar', "ranlib", "ln",
    # Imposed by PyNuSMV
    'python3', 'swig'
]

# The set of library necessary to ensure smooth compilation of the tools
REQUIRED_LIBS = [
    'libexpat'
    # -- these two are optional actually --
    #'libreadline',
    #'libncurses'
]

# Platform specific things
if platform.system() == 'Darwin':
    REQUIRED_TOOLS.append('install_name_tool')
elif platform.system() == 'Linux':
    REQUIRED_TOOLS.append('patchelf')

def is_windows():
    ''':return: True iff the current platform is a windows machine'''
    return platform.system().lower() == 'windows'

def error(message):
    '''
    Prints an error message
    '''
    print("!! ERROR !! {}".format(message), file=sys.stderr)

def is_tool_installed(command):
    '''
    Checks whether the command `command` can be run on the target system.
    '''
    which = 'which' if not is_windows() else 'where'
    return os.system("{} {}".format(which, command)) == 0

def check_required_tools():
    '''
    Checks whether all the required utities are installed on the target host

    :return: True iff all the tools were found to be installed on this host
    '''
    missing = []
    for tool in REQUIRED_TOOLS:
        if not is_tool_installed(tool):
            missing.append(tool)

    if not missing:
        return True
    else:
        error('Some required tools are missing: {}'.format(missing))
        return False

def list_installed_libs(path):
    '''
    Returns the list of all the libraries installed on this system.
    '''
    results = []
    for path, dirs, files in os.walk(path):
        results.extend(files)
    return results

def check_required_libs():
    '''
    Tests the presence of the required libs on the path.
    Concretely, it inspects /usr/lib

    :return: True iff all the libs were found to be installed on this host
    '''
    sys_libs= list_installed_libs("/usr/lib")
    missing = list(filter(lambda x: not any(lib.startswith(x) for lib in sys_libs), REQUIRED_LIBS))

    if not missing:
        return True
    else:
        error('Some required libraries are missing: {}'.format(missing))
        return False


def check_requirements():
    '''
    Checks whether all the required utities are installed on the target host
    '''
    success  = check_required_tools()
    success &= check_required_libs()

    if not success:
        error("Some of the system requirements are not satisfied on your machine")
        sys.exit(1)

if __name__ == '__main__':
    check_requirements()
