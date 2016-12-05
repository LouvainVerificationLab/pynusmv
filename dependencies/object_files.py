'''
# This script lists all the object files which are required to build the
# libnusmv shared library
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: X. Gillard <xavier.gillard [at] uclouvain.be>
'''
from os      import *
from os.path import *

def find_matching(path, extensions, excepted):
    '''
    Recursiveley finds all the files having an exension in `extensions` in
    the subfolders of `path`.

    :param path: the path where to start looking
    :param extensions: the set of all extensions that should be considered while
        searching.
    :param excepted: the name of the files which are excluded from this search
        although they match one of the required extensions
    '''
    results = []

    for elem in listdir(path):
        abs_path = join(path, elem)
        if isfile(abs_path) \
           and any(elem.endswith(ext) for ext in extensions)\
           and elem not in excepted:
            results.append(abs_path)
        elif isdir(abs_path):
            results.extend(find_matching(abs_path, extensions, excepted))

    return results

if __name__ == "__main__":
    excluded     = []#['ltl2smvMain.o', 'HrcNode.o']
    object_files = []
    object_files.extend(find_matching("./NuSMV/NuSMV-2.5.4/nusmv", ['.o'], excluded))
    print(" ".join(object_files))
