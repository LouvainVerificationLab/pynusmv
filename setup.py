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
# Command to build pure python modules
from setuptools.command.build_py   import build_py

import os
import os.path
import shutil

# This configuration simply tells the name of the folder which will contain the
# dependencies sharedlib.
LIB_FOLDER = 'lib'

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

class SharedLib(Command):
    '''
    Additional command for setuptools that builds a sharedlib from all the object
    files present in the given subtree
    '''

    description = 'links compiled artifacts present in the subtree to a sharedlib'
    user_options= [
        ('source-dir=',  's',   'The directory containing the inputs'),
        ('libname='   ,  'l',   'The name of the output library'),
        ('output_dir=',  'o',   'The directory where to place the library'),
        ('libraries=',   'L',   'The set libraries depended upon'),
        ('library-dirs=', None, 'Directories containing the libs when not standard'),
        ('extensions=',  'e',   'The list of extensions of the object files that will be incorporated'),
        ('exclusions=',  'E',   'The list of object files that must be excluded from the output'),
        ('extra-args=',  'a',   'Extra arguments (ie. linker) passed on to gcc')
    ]

    def initialize_options(self):
        self.source_dir   = None
        self.libname      = None
        self.output_dir   = '.'
        self.libraries    = []
        self.library_dirs = []
        self.extensions   = ['.o', '.a']
        self.exclusions   = []
        self.extra_args   = []

    def finalize_options(self):
        pass

    def run(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        result  = os.path.join(self.output_dir, self.sh_libname())
        pattern = "g++ -shared -fPIC {ex_args:} -o {result:} {objects:} {libs:} {dirs:}"
        libs    = " ".join(map(lambda x: '-l'+x, self.libraries))
        dirs    = " ".join(map(lambda x: '-L'+x, self.library_dirs))
        objects = " ".join(self.list_all(self.source_dir))
        ex_args = " ".join(self.extra_args)
        command = pattern.format(result=result, ex_args=ex_args, objects=objects, libs=libs, dirs=dirs)
        print(command)
        os.system(command)

    def sh_libname(self):
        return 'lib{libname:}.so'.format(libname=self.libname)

    def list_all(self, directory):
        result = list()
        for item in os.listdir(directory):
            abs_path = os.path.join(directory, item)

            if os.path.isdir(abs_path):
                result.extend(self.list_all(abs_path))
            elif os.path.isfile(abs_path):
                if any(item.endswith(x) for x in self.extensions):
                    if item not in self.exclusions:
                        result.append(abs_path)

        return result

class FixLoadPath(Command):
    '''
    This command is OSX specific and fixes the load path of some depenency lib
    in all the specified extensions modules. This way, the whole archive can be
    shipped and installed at a site specific location without requiring the user
    to fiddle with his LD_PATH.

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
    description = "OSX specific command to fix the load path of the libdependencies"
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
        return '@loader_path/{}'.format(self.rel_to_target(x))

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
        pattern = 'install_name_tool -change {name:} {loader_path:} {ext:}'
        command = pattern.format(name=self.name,
                                 loader_path=self.loader_path(ext),
                                 ext=ext)
        print(command)
        os.system(command)

    def run(self):
        for ext in self.ext_modules:
            self.fix(ext)

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
        _lib = self.get_finalized_command('sharedlib')
        _lib.source_dir = 'dependencies'
        _lib.libname    = 'dependencies'
        _lib.output_dir = '{}'.format(LIB_FOLDER)
        _lib.libraries  = [ 'expat', 'ncurses', 'readline' ]
        _lib.exclusions = [ 'main.o' ]
        _lib.ex_args    = [ '-headerpad_max_install_names', '-install_name libdependencies.so']
        _lib.run()

        print("Copying the result in {}".format(LIB_FOLDER))
        sh_libname = _lib.sh_libname()
        lib_folder = os.path.join(self.build_lib, LIB_FOLDER)

        # crete the output folder if necessary
        if not os.path.exists(lib_folder):
            os.makedirs(lib_folder)

        # then move the sharedlib over there
        shutil.copyfile(
            os.path.join(_lib.output_dir, sh_libname),
            os.path.join(lib_folder, sh_libname))

        # continue with the regular build_ext
        build_ext.run(self)

        # then fix the generated extensions to make then use the relative loader
        print("Fixing the loader_path")
        _fix = self.get_finalized_command("fix-load-path")
        _fix.name        = 'lib/libdependencies.so'
        _fix.target_path = os.path.join(lib_folder, sh_libname)
        _fix.ext_modules = self.find_ext_modules(self.build_lib)
        _fix.run()


# This is the path to NuSMV header files
INCLUDES  = [
    './dependencies/NuSMV/NuSMV-2.5.4/nusmv',
    './dependencies/NuSMV/NuSMV-2.5.4/nusmv/src',
    './dependencies/NuSMV/NuSMV-2.5.4/cudd-2.4.1.1/include'
]

# These are the libraries dependencies.
LIBRARIES = {
    'libraries'    : ['dependencies']
}

# This is a list of generic arguments that need to be repeated over and over
# for each of the extensions we generate
EXTENSION_ARGS = {
  # The swig specific arguments
  'swig_opts'      : ['-py3'] + [ '-I{}'.format(inc) for inc in INCLUDES ],
  'include_dirs'   : INCLUDES,
  'extra_compile_args': ['-g', '-fPIC'],
  'extra_link_args': ['-Llib', '-headerpad_max_install_names'],
  **LIBRARIES
}

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
      version          = "1.0-RC01",
      author           = "Simon BUSARD, Xavier GILLARD",
      author_email     = "simon.busard@uclouvain.be, xavier.gillard@uclouvain.be",
      url              = "http://lvl.info.ucl.ac.be/Tools/PyNuSMV",
      description      = "Embed NuSMV as a python library",
      ext_modules      = EXTENSIONS,
      packages         = find_packages(),
      install_requires = ['pyparsing'],
      # This is how we actually extend the setuptools framework with extra
      # commands (in particular, we enrich the build_ext command) to take
      # care of building NuSMV and packing it all into a sharedlib called
      # `libdependencies`
      cmdclass    = {
          'make'         : Makefile,
          'sharedlib'    : SharedLib,
          'fix-load-path': FixLoadPath,
          'build_ext'    : BuildExtWithDeps
      }
)
