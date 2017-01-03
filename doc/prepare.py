'''
# This script provides all the necessary logic to prepare the compilation of 
# an up to date pynusmv documentation.
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
import shutil

class DocPrep:
    '''
    This class defines an utility object that prepares the compilation of the 
    documentation so that it can easily be compiled using nothing more than 
    the makefile.
    '''
    
    def __init__(self, version):
        '''
        Creates a new preparator for the documentation build.
        '''
        self.version = version
    
    def replace_in(self, fname, old_str, new_str):
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

    def modules(self, root):
        '''
        Lists all the python modules contained in the `root` package and its sub
        packages.
        
        :param root: the root folder where to start listing the python modules
        '''
        modules = []
        for (parent, folders, files) in os.walk(root):
            # convert relative path to module name
            package = parent.replace("/", ".").lstrip('.') 
            sources = filter(lambda x: x.endswith('.py'), files)
            modules.extend([ package+'.'+mod[:-3] for mod in sources ])
        return modules

    def automodule_rst_snippet(self, module_name):
        '''
        Generates an rst snippet that tells automodule to consider the module
        named after `module_name` while generating the documentation.
        '''
        blank_line= ''
        header    = ':mod:`{}` Module'.format(module_name)
        underline = '-' * len(header)
        automodule= '.. automodule:: {}'.format(module_name)
        pattern   = "\n".join([
            blank_line              ,
            header                  ,
            underline               ,
            blank_line              ,
            automodule              ,
            '    :members:         ',
            '    :undoc-members:   ',
            '    :show-inheritance:',
            blank_line              ,
            ])
        return pattern.format(mod=module_name)
    
    def lower_interface_modules(self, root):
        '''
        Lists all the modules of the lower interface that need to be mocked
        in order to successfully proceed to a build.
        
        This function is different from the above `modules` since it 
        incorporates both the modules (that end up in .i) and their parent since
        they both need to be mocked.
        
        :param root: the place where to start looking.
        '''
        modules = []
        for (parent, folders, files) in os.walk(root):
            # convert relative path to module name
            package = parent.replace("/", ".").lstrip('.') 
            sources = filter(lambda x: x.endswith('.i'), files)
            modules.append(package)
            modules.extend([ package+'.'+mod[:-2] for mod in sources ])
        return modules
    
    def mock_lower_interface_snippet(self):
        '''
        Generates the snippet to automatically mock all the modules from the
        lower interface
        '''
        return "\n".join([
        '                                   ',
        'from unittest.mock import MagicMock',
        'MOCK_MODULES = {modules}           '.format(modules=self.lower_interface_modules('../pynusmv_lower_interface')),
        'sys.modules.update((mod_name, MagicMock()) for mod_name in MOCK_MODULES)',
        '                                   '
        ])

    def run(self):
        # update the documentation config (the version)
        _conftem = "source/conf-template.py"
        _docconf = "source/conf.py"
        shutil.copyfile(_conftem, _docconf)

        self.replace_in(_docconf, "${VERSION}", self.version)
        self.replace_in(_docconf, "${MOCK_LOWER_INTERFACE}", self.mock_lower_interface_snippet())
        
        # list all the modules in pynusmv.rst
        with open("source/pynusmv.rst", 'w') as f:
            header = "\n".join([
                ".. _pynusmv-api: ",
                "                 ",
                "PyNuSMV Reference",
                "*****************",
                "                 "
            ])
            f.write(header)
            
            for mod in self.modules('../pynusmv'):
                f.write(self.automodule_rst_snippet(mod))

if __name__ == '__main__':
    DocPrep('1.0rc4snapshot1').run()
  

