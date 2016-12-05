# -*- encoding: utf-8 -*-
'''
# This script provides a set of functions to perform batch actions on all files
# of a directory tree. These are particularly convenient when it comes to the
# implementation of migration scripts that perform bulk refactoring actions.
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

def replace_in(fname, old_str, new_str):
    '''
    Replace every occurences of `old_str` by `new_str` in the file `fname`.

    :param fname: the path of the file whose content needs to be migrated
    :param old_str: the text before migration
    :param new_str: the text after migration
    '''
    lines = []
    with open(fname, 'r') as f:
        lines =[ line.replace(old_str, new_str) for line in f.readlines() ]

    with open(fname, 'w') as f:
        f.write(''.join(lines))

def foreach_file(path, condition, action):
    '''
    Applies the given `action` to all files satisfying the `condition` in `path`
    and its subdirectories.

    :param path: the directory containig files that might need migration
    :param condition: the condition determining whether or not the action should
        be applied on some given file. (function fname -> Boolean)
    :param action: the action to be applied on the given file.
        (function fname -> anything)
    '''
    for f in os.listdir(path):
        abs_path = os.path.join(path, f)

        if os.path.isfile(abs_path) and condition(abs_path):
            action(abs_path)
        elif os.path.isdir(abs_path):
            foreach_file(abs_path, condition, action)
