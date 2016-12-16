'''
# This script provides all the necessary logic for you to build a distribution
# of pynusmv which you can run on your machine.
#
# This file is part of the pynusmv distribution. As such it is licensed to you
# under the term of the LGPLv2. For more information regarding the legal aspect
# of this licensing, please refer to the full text of the license on the free
# software foundation website.
#
# Author: X. Gillard <xavier.gillard [at] uclouvain.be>
'''
from setuptools                    import setup, find_packages, Command
from setuptools.extension          import Extension
# Command to build native extentions
from setuptools.command.build_ext  import build_ext
# Command to perform a build then run the tests
from setuptools.command.test       import test

import os
import os.path
import shutil
import platform
import subprocess

# This configuration lets you update the version of the package without having
# to scroll down for about 1k lines of codes.
VERSION    = '1.0rc3'
# This configuration simply tells the name of the folder which will contain the
# dependencies sharedlib.
LIB_FOLDER = 'lib'

class SharedLibBuilder:
    '''
    This class is a simple builder that I developed to ease the creation of the
    `depenedencies` shared library used to embody all of the NuSMV, CUDD and
    SAT solvers code.
    '''
    def __init__(self, fname):
        '''
        Initializes a new builder instance.

        :param fname: the name of the file to be produced.

        .. warning::
            If you intend to create the lib in a folder other than the current
            one, you will need to create it first.
        '''
        self._fname = fname
        self._libs  = []
        self._obj   = []

    def depending_on(self, *libs):
        '''
        Defines the libraries that _might_ be necessary to the sharedlib creation
        if they are installed on the target system.

        :param libs: a list of libraries that might be required by the objects
            contained in the produced library.
        :return: self to allow chaining
        '''
        self._libs.extend(libs)
        return self

    def require(self, what, where, excluding=[]):
        '''
        Defines what should constitute the body of the sharedlib.

        :param what: the extension of the files that need to be combined into the lib.
        :param where: the location where to (recursively) search for files having the extension `what`.
        :param excluding: the name of objects that must explicitly be ignored by the build process.
        :return: self to allow function call chaining.
        '''
        self._obj.append( (where, what, excluding) )
        return self

    def lib_not_found(self):
        '''
        :return: the distinctive message that is used to decide whether or not
        some library is installed on the target system.
        '''
        OSX  = "library not found"
        LINUX= "cannot find -l"
        return LINUX if platform.system() == 'Linux' else OSX

    def is_lib_installed(self, libname):
        '''
        :return: True iff libname is a system library available at link time
        '''
        cmd = "ld -l{}".format(libname)
        sub = subprocess.run(cmd, shell=True, check=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return self.lib_not_found() not in str(sub.stderr)

    def list_artifacts(self, what, where, excl):
        '''
        :return: the list of objects with extention `what` in the subtree of `where`
        having a name different from those in `excl`.

        :param what: the extension of the files that need to be combined into the lib.
        :param where: the location where to (recursively) search for files having the extension `what`.
        :param excl: the name of objects that must explicitly be ignored by the build process.
        '''
        results = []
        for path, dirs, files in os.walk(where):
            fnames   = filter(lambda x: x.endswith(what) and x not in excl, files)
            artifacts= [ os.path.join(path, fname) for fname in fnames ]
            results.extend(artifacts)
        return results

    def platform_dependent_flags(self):
        '''
        :return: some platform dependent flags which help getting an useful output
        '''
        return "-Wl,--no-as-needed" if platform.system() == 'Linux' else ''

    def get_command(self):
        '''
        :return: the potentially very long command which is used to actually
        generate the shared library
        '''
        libraries = ["-l{}".format(l) for l in filter(lambda x: self.is_lib_installed(x), self._libs) ]
        objects = [ obj for (where,what, excl) in self._obj for obj in self.list_artifacts(what, where, excl) ]

        pattern = "g++ -shared -fPIC {flags:} -o {fname:} {libs:} {objects:}"
        command = pattern.format(
                            fname   = self._fname,
                            flags   = self.platform_dependent_flags(),
                            libs    = " ".join(libraries),
                            objects = " ".join(objects))
        return command

    def build(self):
        '''
        Actually proceeds to the build of the sharedlib.
        '''
        os.system(self.get_command())

# The coming classes define new (custom) commands that extend the ones available
# in setuptools. The goal of these commands is to generate a sharedlib containing
# all the code of NuSMV necessary for the extensions composing the lower interface
# to link with.
class Makefile(Command):
    '''
    Additional command for setuptools that executes some Makefile
    '''
    description = 'This command executes the desired `makefile`.'
    user_options= [
        ('source-dir=', 's',   'The directory containing the Makefile'),
        ('target=',      None, 'The target to be executed')
    ]

    def initialize_options(self):
        self.source_dir = '.'
        self.target     = ''

    def finalize_options(self):
        pass

    def run(self):
        pattern = 'make -C {src_dir:} {target:}'
        command = pattern.format(src_dir=self.source_dir, target=self.target)
        os.system(command)

class FixLoadPath(Command):
    '''
    This command is platform dependent and fixes the load path of some depenency
    lib in all the specified extensions modules. This way, the whole archive can
    be shipped and installed at a site specific location without requiring the
    user to fiddle with his LD_PATH.

    .. Note::
        On OS X, this command executes a call to `install_name_tool` and
        on Linux, it executes a call to `patchelf`.

        To verify the effectiveness of the load path patching, one can use the
        following commands:
            * `otool -L <lib>` on OSX
            * `ldd <lib>` on Linux

    .. Note::
        Proceeding this way is certainly not the cleanest approach from a
        conceptual point of view but it turns out that it DOES WORKS !
        I tried so many different options that I cant remember them all but
        the bottomline is: I don't like this hack either but distutils
        and setuptools are not going to help you creating a cleaner solution.

        The data file approach simply doesn't work

        Statically linking all the extensions with nusmv code does not work
        since NuSMV needs global state which is not shared when the extensions embed
        NuSMV code.

        Plugging an extr bit of code into the shared lib to turn it into a python
        extension is also doomed to fail since the other extensions do not realize
        that the symbols they need have already been loaded into memory (even after
        the pseudo-ext is loaded)

        Making a big blob with all the NuSMV code and compile it all into one single
        python extension is both _unmaintainable_ and is _SO HUGE_ that swig isn't
        able to deal with it (fails with exit code 2).

        Passing the `runtime_library_dirs` to the extensions do not work on OSX.
    '''
    description = "Platform specific command to fix the load path of the libdependencies"
    user_options= [
        ('name=',        'n', 'The name of the library as it has been written in the shared object'),
        ('target-path=', 't', 'The path the targetted shared object (the one to refer to)'),
        ('ext-modules=', 'm', 'The extension modules that needs to be fixed')
    ]

    def initialize_options(self):
        self.name        = None
        self.target_path = None
        self.ext_modules = []

    def finalize_options(self):
        pass

    def rel_to_target(self, x):
        extdir = os.path.dirname(x)
        return os.path.relpath(self.target_path, extdir)

    def loader_path(self, x):
        if platform.system() == 'Darwin':
            return '@loader_path/{}'.format(self.rel_to_target(x))
        if platform.system() == 'Linux':
            return "'$ORIGIN/{}'".format(os.path.dirname(self.rel_to_target(x)))

        raise ValueError('Unsupported platform')

    def command_pattern(self):
        if platform.system() == 'Darwin':
            return 'install_name_tool -change {name:} {loader_path:} {ext:}'
        if platform.system() == 'Linux' :
            return 'patchelf --set-rpath {loader_path:} {ext:}'

        raise ValueError('Unsupported platform')


    def fix(self, ext):
        '''
        Adapts the linking of the dynamic libraries to allow the use of a
        relative path between the ext to fix and the target library.

        .. Note::
            The following resources have been really useful and/or inspirational
                - http://conda.pydata.org/docs/building/shared-libraries.html
                - http://apple.co/2hcSLFx
                - http://stackoverflow.com/questions/4513799/how-to-set-the-runtime-path-rpath-of-an-executable-with-gcc-under-mac-osx
                - setup.py in http://effbot.org/downloads/Imaging-1.1.7.tar.gz
                - https://docs.python.org/3.5/extending/extending.html (even if this one led to a dead end)
        '''
        pattern = self.command_pattern()
        command = pattern.format(name=self.name,
                                 loader_path=self.loader_path(ext),
                                 ext=ext)
        print(command)
        os.system(command)

    def run(self):
        for ext in self.ext_modules:
            self.fix(ext)

class GenerateInitFiles(Command):
    '''
    This command generates some `__init__` file for all the modules of the
    lower interface.
    '''
    description = 'Generates `__init__` files for all the modules of the lower interface'
    user_options= []

    HEADER_TEXT= "''' \n" + \
    "# This packages provides an access to all the low level functionalities of NuSMV. \n" + \
    "# These functions consist of the raw APIs wrapped with a thin SWIG layer that \n" + \
    "# makes them useable in python. \n" + \
    "# \n" + \
    "# The code of the submodules composing this packages is structured so as to \n" + \
    "# closely resemble that of the original NuSMV project. \n" + \
    "# \n" + \
    "# This file is part of the pynusmv distribution. As such it is licensed to you \n" + \
    "# under the term of the LGPLv2. For more information regarding the legal aspect \n" + \
    "# of this licensing, please refer to the full text of the license on the free \n" + \
    "# software foundation website. \n" + \
    "# \n" + \
    "# Author: S. Busard  <simon.busard   [at] uclouvain.be> \n" + \
    "#         X. Gillard <xavier.gillard [at] uclouvain.be> \n" + \
    "''' \n\n"

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def get_all_var(self, directory):
        '''
        :return: the list of all elements that should be listed in the `all` var
        '''
        # Complete the header file overriding the 'all' variable.
        ## For the swigged interfaces
        _swig = filter(lambda x: x.endswith(".i"), os.listdir(directory))
        _swig = [ x[:-2] for x in _swig ]
        ## For the subdirectories
        _dirs = list(filter(lambda x: os.path.isdir(os.path.join(directory, x)), os.listdir(directory)))
        _dirs = list(filter(lambda x: x!='__pycache__', _dirs))
        _all  = _swig + _dirs
        return _all

    def create_init_scripts(self, directory):
        # Start creating the init script in the current folder
        init_script = os.path.join(directory, '__init__.py')
        if not os.path.exists(init_script):
            with open(init_script, 'w') as f:
                f.write(GenerateInitFiles.HEADER_TEXT)
                _all = self.get_all_var(directory)
                f.write("all = {}".format(_all))

        # Then do the same for all the sub folders
        for item in os.listdir(directory):
            abs_path = os.path.join(directory, item)
            if os.path.isdir(abs_path) :
                self.create_init_scripts(abs_path)

    def run(self):
        self.create_init_scripts('pynusmv_lower_interface')


class CopySwiggedModules(Command):
    '''
    This extension makes sure that every python module generated by SWIG gets
    copied over to the build destination. This is mostly required because in
    case of partial build (only the ext. needs to be rebuilt), the output dist
    does not contain these modules.
    '''
    description = "Makes sure that the swigged python module are copied to their build location"
    user_options= [
        ('source', 's', 'The source location containing the modules to be recursively copied'),
        ('target', 't', 'The target location where to copy the files before packaging')
    ]

    def initialize_options(self):
        self.source = None
        self.target = None

    def finalize_options(self):
        pass

    def copy_all(self, directory):
        _here = os.path.join(self.source, directory)
        _there= os.path.join(self.target, directory)

        for item in os.listdir(_here):
            _src = os.path.join(_here, item)
            _dst = os.path.join(_there,item)

            if os.path.isfile(_src) and _src.endswith('.py'):
                if not os.path.exists(_there):
                    os.makedirs(_there)
                shutil.copyfile(_src, _dst)
            elif os.path.isdir(_src):
                self.copy_all(os.path.join(directory, item))

    def run(self):
        self.copy_all("")


class BuildExtWithDeps(build_ext):
    '''
    This command extends build_ext to make sure the dependencies are built
    and packs them into a sharedlib which can then be used to link with other
    extensions.

    .. Note::
        The sharedlib is called `libdependencies` and is located in `../LIB_FOLDER`
    '''
    def find_ext_modules(self, directory):
        result = list()
        for item in os.listdir(directory):
            abs_path = os.path.join(directory, item)

            if os.path.isdir(abs_path):
                result.extend(self.find_ext_modules(abs_path))
            elif os.path.isfile(abs_path) and item.endswith('.so'):
                result.append(abs_path)
        return result

    def run(self):
        print("Making the dependencies")
        _make = self.get_finalized_command('make')
        _make.source_dir = 'dependencies'
        _make.run()


        print("Packing them in a shared library")
        library_soname= "libdependencies.so"
        library_fname = os.path.join(LIB_FOLDER, library_soname)

        if not os.path.exists(LIB_FOLDER):
            os.makedirs(LIB_FOLDER)

        SharedLibBuilder(library_fname)\
            .depending_on("expat", "ncurses", "readline")\
            .require('.o', "dependencies/NuSMV/NuSMV-2.5.4/nusmv", ['main.o'])\
            .require('.a', "dependencies/NuSMV/NuSMV-2.5.4/cudd-2.4.1.1")\
            .require('.a', "dependencies/MiniSat/minisat")\
            .build()

        print("Copying the result in {}".format(LIB_FOLDER))
        lib_folder = os.path.join(self.build_lib, LIB_FOLDER)

        # crete the output folder if necessary
        if not os.path.exists(lib_folder):
            os.makedirs(lib_folder)

        # then move the sharedlib over there
        shutil.copyfile(
            os.path.join(LIB_FOLDER, library_soname),
            os.path.join(lib_folder, library_soname))

        # continue with the regular build_ext
        build_ext.run(self)

        # then fix the generated extensions to make then use the relative loader
        print("Fixing the loader_path")
        _fix = self.get_finalized_command("fix-load-path")
        _fix.name        = library_fname
        _fix.target_path = os.path.join(lib_folder, library_soname)
        _fix.ext_modules = self.find_ext_modules(self.build_lib)
        _fix.run()

        # Generate init scripts for each of the modules composing the lower intf
        print("Generate init files for modules of the lower interface")
        self.get_finalized_command("mk_init").run()

        # make sure the swigged python module are copied where they need
        print("Copying the swigged python modules")
        _cpy = self.get_finalized_command("copy_swig_mod")
        _cpy.source = "pynusmv_lower_interface"
        _cpy.target = os.path.join(self.build_lib, "pynusmv_lower_interface")
        _cpy.run()

class Doc(Command):
    '''
    Generates the documentation in the usual build directory
    '''
    description = 'Generates the project documentation'
    user_options= [
        ("build-dir=", None, "The location of the build directory where to copy the docs"),
        ("builder="  , None, "The sphinx builder to use to generate the docs")
    ]

    def initialize_options(self):
        self.builder  = 'html'
        self.build_dir= None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_lib', 'build_dir') )

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

    def run(self):
        # The complete system needs to be built before we can proceed to
        # documentation generation
        self.get_finalized_command('build').run()

        # ensure it can be done
        if not os.path.exists(self.build_dir):
            os.makedirs(self.build_dir)

        # it cant already exist: delete it if needed
        _doc = os.path.join(self.build_dir, "doc")
        if os.path.exists(_doc):
            shutil.rmtree(_doc)

        # copy the doc folder to the build location
        shutil.copytree("doc", _doc)

        # update the documentation config (the version)
        _docconf = os.path.join(_doc, "source/conf.py")
        self.replace_in(_docconf, "${VERSION}", VERSION)

        # use the makefile to effectively generate the docs
        pattern = "cd {build_dir:} ; make -C doc {builder:}"
        command = pattern.format(build_dir=self.build_dir, builder=self.builder)
        os.system(command)

        # package the documentation in a zip file that can easily be uploaded
        # on PyPI for public sharing
        shutil.make_archive("dist/doc", "zip", os.path.join(_doc, "html"))

class Clean(Command):
    '''
    This command cleans up everything that was generated during the compilation
    phase.
    '''
    description    = "Deletes all the compilation-generated artifacts"
    user_options   = [
        ('no-dist', None, 'Do not clean the distribution files (dist folder)'),
        ('no-deps', None, 'Do not clean the dependencies')
    ]

    # The set of extensions of the files generated by swig
    SWIG_GENERATED = ['.c', '.h', '.py', '.so']

    def initialize_options(self):
        self.no_dist = False
        self.no_deps = False

    def finalize_options(self):
        pass

    def rm_rf(self, path):
        '''
        This function has the same effect as calling "rm -rf `path`" on a unix
        system. That is to say, it recursively removes all the content under
        `path`.

        .. Note::
            This function silently swallows exception that can be raised during
            the deletion. Hence, it offers no guarantee regarding the successful
            removal of the subtree of the file system.
        '''
        try:
            for item in os.listdir(path):
                abs_path = os.path.join(path, item)
                if os.path.isdir(abs_path):
                    self.rm_rf(abs_path)
                elif os.path.isfile(abs_path):
                    os.remove(abs_path)
            os.rmdir(path)
        except:
            # No need to whine then the target does not exist
            pass

    def is_swig_generated(self, fname):
        ''':return: True iff `fname` denotes a file that has been generated by swig'''
        return any(fname.endswith(ext) for ext in Clean.SWIG_GENERATED)

    def remove_swig_artifacts(self, path):
        '''
        Removes all the artifacts that have been generated by swig during the
        build_ext phase.

        .. Note::
            This function silently swallows exception that can be raised during
            the deletion. Hence, it offers no guarantee regarding the successful
            removal of the subtree of the file system.
        '''
        try:
            for item in os.listdir(path):
                abs_path = os.path.join(path, item)
                if os.path.isfile(abs_path) and self.is_swig_generated(item):
                    os.remove(abs_path)
                elif os.path.isdir(abs_path):
                    self.remove_swig_artifacts(abs_path)
        except:
            # silently swallow the exceptions (if it cant be cleaned.. so be it)
            pass

    def remove_pycaches(self, directory):
        '''
        This method recursively deletes all the `__pycache__` encountered in the
        python codebase.
        '''
        for item in os.listdir(directory):
            abs_path = os.path.join(directory, item)
            if os.path.isdir(abs_path):
                if item == '__pycache__':
                    self.rm_rf(abs_path)
                else:
                    self.remove_pycaches(abs_path)

    def clean_dependencies(self):
        _make = self.get_finalized_command('make')
        _make.source_dir = 'dependencies'
        _make.target     = 'clean'
        _make.run()

    def run(self):
        # Delete the dependencies
        if not self.no_deps:
            print("Cleaning the dependencies")
            self.clean_dependencies()

        # Delete the dist files
        if not self.no_dist:
            print("Cleaning up the distribution (dist folder)")
            self.rm_rf("dist")

        # Delete the lib folder
        print("Deleting the lib folder")
        self.rm_rf('lib')

        # Delete the lower interface .h, .c, .so, .py
        print("Removing all swig generated files")
        self.remove_swig_artifacts('pynusmv_lower_interface')

        # Delete the build folder content
        print("Deleting the build folder")
        self.rm_rf('build')

        # Delete the egg-info
        print("Deleting the build folder")
        self.rm_rf('pynusmv.egg-info')

        # Delete the __pycache__
        print("Deleting the build __pycache__ s")
        self.remove_pycaches('pynusmv')
        self.remove_pycaches('pynusmv_lower_interface')
        self.remove_pycaches('tests')


class BuildAndTest(test):
    '''
    This command overrides the default one and performs a full build before
    to run the unittests of the project. (default command performs an inplace
    build)
    '''
    description = 'Performs a complete build then run the unit tests'

    def run(self):
        '''
        Overrides setuptools.command.test.test.run to perform a complete build
        '''
        self.get_finalized_command("build").run()
        test.run(self)

class ListPackages(Command):
    '''
    This command is a plain utility command that does not participate in the
    build and only serves the purpose of conveniently listing the python packages
    that are packed in the distribution archive.
    '''
    description = "Prints the list of python packages that will be part of the distribution"
    user_options= []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        for pkg in find_packages():
            print("- {}".format(pkg))


# This is the path to NuSMV header files
INCLUDES  = [
    './dependencies/NuSMV/NuSMV-2.5.4/nusmv',
    './dependencies/NuSMV/NuSMV-2.5.4/nusmv/src',
    './dependencies/NuSMV/NuSMV-2.5.4/cudd-2.4.1.1/include'
]

# These are the libraries dependencies.
LIBRARIES = {
    'libraries' : ['dependencies']
}

# This is a list of generic arguments that need to be repeated over and over
# for each of the extensions we generate
EXTENSION_ARGS = {
  # The swig specific arguments
  'swig_opts'         : ['-py3'] + [ '-I{}'.format(inc) for inc in INCLUDES ],
  'include_dirs'      : INCLUDES,
  'extra_compile_args': ['-g', '-fPIC'],
  'extra_link_args'   : ['-Llib'],
  **LIBRARIES
}

# Plug-in the platform specific linking flags
if platform.system() == 'Darwin':
    # OSX specific
    EXTENSION_ARGS['extra_link_args'].append('-headerpad_max_install_names')

if platform.system() == 'Linux':
    EXTENSION_ARGS['extra_compile_args'].append('-Wl,--no-as-needed')

# In the coming lines, we define all the extensions composing the lower
# interface of pynusmv. These are all generated using swig.
EXTENSIONS = [
    Extension(
        'pynusmv_lower_interface.nusmv.addons_core._addons_core',
        sources=['pynusmv_lower_interface/nusmv/addons_core/addons_core.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.addons_core.compass._compass',
        sources=['pynusmv_lower_interface/nusmv/addons_core/compass/compass.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.addons_core.compass.compile._compile',
        sources=['pynusmv_lower_interface/nusmv/addons_core/compass/compile/compile.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.addons_core.compass.parser.ap._ap',
        sources=['pynusmv_lower_interface/nusmv/addons_core/compass/parser/ap/ap.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.addons_core.compass.parser.prob._prob',
        sources=['pynusmv_lower_interface/nusmv/addons_core/compass/parser/prob/prob.i'],
        **EXTENSION_ARGS),

    # be module
    Extension(
        'pynusmv_lower_interface.nusmv.be._be',
        sources=['pynusmv_lower_interface/nusmv/be/be.i'],
        **EXTENSION_ARGS),

    # bmc modules
    Extension(
        'pynusmv_lower_interface.nusmv.bmc._bmc',
        sources=['pynusmv_lower_interface/nusmv/bmc/bmc.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.bmc.sbmc._sbmc',
        sources=['pynusmv_lower_interface/nusmv/bmc/sbmc/sbmc.i'],
        **EXTENSION_ARGS),

    # cinit module
    Extension(
        'pynusmv_lower_interface.nusmv.cinit._cinit',
        sources=['pynusmv_lower_interface/nusmv/cinit/cinit.i'],
        **EXTENSION_ARGS),

    # cmd module
    Extension(
        'pynusmv_lower_interface.nusmv.cmd._cmd',
        sources=['pynusmv_lower_interface/nusmv/cmd/cmd.i'],
        **EXTENSION_ARGS),

    # compile modules
    Extension(
        'pynusmv_lower_interface.nusmv.compile._compile',
        sources=['pynusmv_lower_interface/nusmv/compile/compile.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.compile.symb_table._symb_table',
        sources=['pynusmv_lower_interface/nusmv/compile/symb_table/symb_table.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.compile.type_checking._type_checking',
        sources=['pynusmv_lower_interface/nusmv/compile/type_checking/type_checking.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.compile.type_checking.checkers._checkers',
        sources=['pynusmv_lower_interface/nusmv/compile/type_checking/checkers/checkers.i'],
        **EXTENSION_ARGS),

    # dag module
    Extension(
        'pynusmv_lower_interface.nusmv.dag._dag',
        sources=['pynusmv_lower_interface/nusmv/dag/dag.i'],
        **EXTENSION_ARGS),

    # dd module
    Extension(
        'pynusmv_lower_interface.nusmv.dd._dd',
        sources=['pynusmv_lower_interface/nusmv/dd/dd.i'],
        **EXTENSION_ARGS),

    # enc modules
    Extension(
        'pynusmv_lower_interface.nusmv.enc._enc',
        sources=['pynusmv_lower_interface/nusmv/enc/enc.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.enc.base._base',
        sources=['pynusmv_lower_interface/nusmv/enc/base/base.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.enc.bdd._bdd',
        sources=['pynusmv_lower_interface/nusmv/enc/bdd/bdd.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.enc.be._be',
        sources=['pynusmv_lower_interface/nusmv/enc/be/be.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.enc.bool._bool',
        sources=['pynusmv_lower_interface/nusmv/enc/bool/bool.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.enc.utils._utils',
        sources=['pynusmv_lower_interface/nusmv/enc/utils/utils.i'],
        **EXTENSION_ARGS),

    # fsm modules
    Extension(
        'pynusmv_lower_interface.nusmv.fsm._fsm',
        sources=['pynusmv_lower_interface/nusmv/fsm/fsm.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.fsm.bdd._bdd',
        sources=['pynusmv_lower_interface/nusmv/fsm/bdd/bdd.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.fsm.be._be',
        sources=['pynusmv_lower_interface/nusmv/fsm/be/be.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.fsm.sexp._sexp',
        sources=['pynusmv_lower_interface/nusmv/fsm/sexp/sexp.i'],
        **EXTENSION_ARGS),

    # hrc modules
    Extension(
        'pynusmv_lower_interface.nusmv.hrc._hrc',
        sources=['pynusmv_lower_interface/nusmv/hrc/hrc.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.hrc.dumpers._dumpers',
        sources=['pynusmv_lower_interface/nusmv/hrc/dumpers/dumpers.i'],
        **EXTENSION_ARGS),

    # ltl modules
    Extension(
        'pynusmv_lower_interface.nusmv.ltl._ltl',
        sources=['pynusmv_lower_interface/nusmv/ltl/ltl.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.ltl.ltl2smv._ltl2smv',
        sources=['pynusmv_lower_interface/nusmv/ltl/ltl2smv/ltl2smv.i'],
        **EXTENSION_ARGS),

    # mc module
    Extension(
        'pynusmv_lower_interface.nusmv.mc._mc',
        sources=['pynusmv_lower_interface/nusmv/mc/mc.i'],
        **EXTENSION_ARGS),

    # node modules
    Extension(
        'pynusmv_lower_interface.nusmv.node._node',
        sources=['pynusmv_lower_interface/nusmv/node/node.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.node.normalizers._normalizers',
        sources=['pynusmv_lower_interface/nusmv/node/normalizers/normalizers.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.node.printers._printers',
        sources=['pynusmv_lower_interface/nusmv/node/printers/printers.i'],
        **EXTENSION_ARGS),

    # opt module
    Extension(
        'pynusmv_lower_interface.nusmv.opt._opt',
        sources=['pynusmv_lower_interface/nusmv/opt/opt.i'],
        **EXTENSION_ARGS),

    # parser modules
    Extension(
        'pynusmv_lower_interface.nusmv.parser._parser',
        sources=['pynusmv_lower_interface/nusmv/parser/parser.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.parser.idlist._idlist',
        sources=['pynusmv_lower_interface/nusmv/parser/idlist/idlist.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.parser.ord._ord',
        sources=['pynusmv_lower_interface/nusmv/parser/ord/ord.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.parser.psl._psl',
        sources=['pynusmv_lower_interface/nusmv/parser/psl/psl.i'],
        **EXTENSION_ARGS),

    # prop module
    Extension(
        'pynusmv_lower_interface.nusmv.prop._prop',
        sources=['pynusmv_lower_interface/nusmv/prop/prop.i'],
        **EXTENSION_ARGS),

    # rbc modules
    Extension(
        'pynusmv_lower_interface.nusmv.rbc._rbc',
        sources=['pynusmv_lower_interface/nusmv/rbc/rbc.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.rbc.clg._clg',
        sources=['pynusmv_lower_interface/nusmv/rbc/clg/clg.i'],
        **EXTENSION_ARGS),

    # sat module
    Extension(
        'pynusmv_lower_interface.nusmv.sat._sat',
        sources=['pynusmv_lower_interface/nusmv/sat/sat.i'],
        **EXTENSION_ARGS),

    # set module
    Extension(
        'pynusmv_lower_interface.nusmv.set._set',
        sources=['pynusmv_lower_interface/nusmv/set/set.i'],
        **EXTENSION_ARGS),

    # sexp module
    Extension(
        'pynusmv_lower_interface.nusmv.sexp._sexp',
        sources=['pynusmv_lower_interface/nusmv/sexp/sexp.i'],
        **EXTENSION_ARGS),

    # simulate module
    Extension(
        'pynusmv_lower_interface.nusmv.simulate._simulate',
        sources=['pynusmv_lower_interface/nusmv/simulate/simulate.i'],
        **EXTENSION_ARGS),

    # trace modules
    Extension(
        'pynusmv_lower_interface.nusmv.trace._trace',
        sources=['pynusmv_lower_interface/nusmv/trace/trace.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.trace.eval._eval',
        sources=['pynusmv_lower_interface/nusmv/trace/eval/eval.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.trace.exec_._exec_',
        sources=['pynusmv_lower_interface/nusmv/trace/exec_/exec_.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.trace.loaders._loaders',
        sources=['pynusmv_lower_interface/nusmv/trace/loaders/loaders.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.trace.plugins._plugins',
        sources=['pynusmv_lower_interface/nusmv/trace/plugins/plugins.i'],
        **EXTENSION_ARGS),

    # trans modules
    Extension(
        'pynusmv_lower_interface.nusmv.trans._trans',
        sources=['pynusmv_lower_interface/nusmv/trans/trans.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.trans.bdd._bdd',
        sources=['pynusmv_lower_interface/nusmv/trans/bdd/bdd.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.trans.generic._generic',
        sources=['pynusmv_lower_interface/nusmv/trans/generic/generic.i'],
        **EXTENSION_ARGS),

    # utils module
    Extension(
        'pynusmv_lower_interface.nusmv.utils._utils',
        sources=['pynusmv_lower_interface/nusmv/utils/utils.i'],
        **EXTENSION_ARGS),

    # wff modules
    Extension(
        'pynusmv_lower_interface.nusmv.wff._wff',
        sources=['pynusmv_lower_interface/nusmv/wff/wff.i'],
        **EXTENSION_ARGS),

    Extension(
        'pynusmv_lower_interface.nusmv.wff.w2w._w2w',
        sources=['pynusmv_lower_interface/nusmv/wff/w2w/w2w.i'],
        **EXTENSION_ARGS)
]

#
setup(name             = 'pynusmv',
      version          = VERSION,
      author           = "Simon BUSARD, Xavier GILLARD",
      author_email     = "simon.busard@uclouvain.be, xavier.gillard@uclouvain.be",
      url              = "http://lvl.info.ucl.ac.be/Tools/PyNuSMV",
      description      = "Embed NuSMV as a python library",
      keywords         = 'Symbolic model checking, Epistemic logic, Tools',
      classifiers      = [
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)'
      ],
      ext_modules      = EXTENSIONS,
      packages         = find_packages(),
      install_requires = ['pyparsing'],
      # This is how we actually extend the setuptools framework with extra
      # commands (in particular, we enrich the build_ext command) to take
      # care of building NuSMV and packing it all into a sharedlib called
      # `libdependencies`
      cmdclass    = {
          # overridden commands
          'build_ext'    : BuildExtWithDeps,
          'test'         : BuildAndTest,
          'clean'        : Clean,
          # additional / custom / esoteric stuffs
          'doc'          : Doc,
          'list_packages': ListPackages,
          'make'         : Makefile,
          'fix-load-path': FixLoadPath,
          'mk_init'      : GenerateInitFiles,
          'copy_swig_mod': CopySwiggedModules
      }
)
