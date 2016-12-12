import os
import os.path

HEADER_TEXT= """'''
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
"""

def create_init_scripts(directory):
    # Start creating the init script in the current folder
    init_script = os.path.join(directory, '__init__.py')
    if not os.path.exists(init_script):
        with open(init_script, 'w') as f:
            f.write(HEADER_TEXT)
            # Complete the header file overriding the 'all' variable.
            ## For the swigged interfaces
            _swig = filter(lambda x: x.endswith(".i"), os.listdir(directory))
            _swig = [ x[:-2] for x in _swig ]
            ## For the subdirectories
            _dirs = list(filter(lambda x: os.path.isdir(os.path.join(directory, x)), os.listdir(directory)))
            _dirs = list(filter(lambda x: x!='__pycache__', _dirs))
            _all  = _swig + _dirs
            f.write("all = {}".format(_all))

    # Then do the same for all the sub folders
    for item in os.listdir(directory):
        abs_path = os.path.join(directory, item)
        if os.path.isdir(abs_path) :
            create_init_scripts(abs_path)

if __name__ == "__main__":
    create_init_scripts("pynusmv_lower_interface")
