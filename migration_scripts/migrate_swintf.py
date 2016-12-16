# -*- encoding: utf-8 -*-
'''
# This script implements a migration step that 'refactors' the SWIG interface
# source files (.i) to make sure these can compile against the source file of
# NuSMV + CUDD which resides in the dependencies folder.
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: X. Gillard <xavier.gillard [at] uclouvain.be>
'''
from batch_utils import *

def is_swig_interface(fname):
    ''':return: True iff `fname` is a swig interface file'''
    return fname.endswith('.i')

def migrate_nusmv_refs(fname):
    '''
    Replaces all references to nusmv to the one in the dependencies folder
    '''
    old_txt = '../../../nusmv/'
    new_txt = '../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/'

    return replace_in(fname, old_txt, new_txt)

def migrate_cudd_refs(fname):
    '''
    Replaces all references to cudd to the one in the dependencies folder
    '''
    old_txt = '../../../cudd-2.4.1.1/'
    new_txt = '../../../dependencies/NuSMV/NuSMV-2.5.4/cudd-2.4.1.1/'

    return replace_in(fname, old_txt, new_txt)

def migrate_refs(fname):
    '''
    Compound function that applies both references update::
         - the one for NuSMV and
         - the one for CUDD
    '''
    migrate_nusmv_refs(fname)
    migrate_cudd_refs(fname)

if __name__ == '__main__':
    foreach_file('pynusmv', is_swig_interface, migrate_refs)
