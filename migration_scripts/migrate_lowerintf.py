# -*- encoding: utf-8 -*-
'''
# This script implements a migration step that 'refactors' the python modules in
# pynusmv to make them use the lower interface in the 'new' package rather than
# the sub package under pynusmv (although this was conceptually nice, setuptools
# wouldn't package it that way).
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: X. Gillard <xavier.gillard [at] uclouvain.be>
'''
from batch_utils import *

def migrate_pynusmv_nusmv_refs(fname):
    '''
    Replaces all occurrences of a reference to pynusmv.nusmv in the source code
    by one referring to pynusmv_lower_interface
    '''
    old_txt = 'pynusmv.nusmv.'
    new_txt = 'pynusmv_lower_interface.nusmv.'
    return replace_in(fname, old_txt, new_txt)

def migrate_nusmv_refs(fname):
    '''
    Replaces all occurrences of a reference to .nusmv in the source code
    by one referring to pynusmv_lower_interface
    '''
    old_txt = 'from .nusmv.'
    new_txt = 'from pynusmv_lower_interface.nusmv.'
    return replace_in(fname, old_txt, new_txt)

def migrate_refs(fname):
    '''
    Compound function that applies both migration steps::
        - pynusmv.
        - .nusmv.
    '''
    migrate_pynusmv_nusmv_refs(fname)
    migrate_nusmv_refs(fname)

def is_python(fname):
    ''':return: True iff `fname` designates a python file'''
    return fname.endswith('.py')

def is_swig(fname):
    ''':return: True iff `fname` designates a SWIG interface file'''
    return fname.endswith('.i')

def is_source(fname):
    return is_python(fname) or is_swig(fname)

if __name__ == '__main__':
    foreach_file('tests', is_python, migrate_refs)
