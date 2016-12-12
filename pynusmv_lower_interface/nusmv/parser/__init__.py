'''
# This packages provides an access to all the low level functionalities of NuSMV.
# These functions consist of the raw APIs wrapped with a thin SWIG layer that
# makes them useable in python.
#
# The code of the submodules composing this packages is structured so as to
# closely resemble that of the original NuSMV project.
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: S. Busard  <simon.busard   [at] uclouvain.be>
#         X. Gillard <xavier.gillard [at] uclouvain.be>
'''
all = ['parser', 'idlist', 'ord', 'psl']