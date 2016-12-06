
from setuptools           import setup, find_packages
from setuptools.extension import Extension
import os
import os.path

# Make sure the NuSMV binaries are built and the static libs created.
os.system('make -C ./dependencies')

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

def is_static_lib(fname):
    ''':return: True iff `fname` denotes a static library'''
    basename = os.path.basename(fname)
    return basename.startswith('lib')  \
           and basename.endswith('.a') \
           and not os.path.islink(fname)

def memoize_info(fname, lib_names, lib_dirs, extra_objects):
    basename = os.path.basename(fname)
    # strips off the 'lib' part of the name
    libname = basename[3:-2]
    if libname not in lib_names:
        lib_names.append(libname)
    # memoize the enclosing directory
    libdir  = os.path.dirname(fname)
    if libdir not in lib_dirs:
        lib_dirs.append(libdir)
    # memoize the static lib file
    if fname not in extra_objects:
        extra_objects.append(fname)

def libraries_info():
    libnames        = ['expat']
    libdirs         = []
    extra_objects   = []
    memoize_libinfo = lambda x: memoize_info(x, libnames, libdirs, extra_objects)
    foreach_file('./dependencies', is_static_lib, memoize_libinfo)
    return {
        'libraries'    : libnames,
        'library_dirs' : libdirs ,
        'extra_objects': extra_objects }

# This is the path to NuSMV binaries
INCLUDES  = [
    './dependencies/NuSMV/NuSMV-2.5.4/nusmv',
    './dependencies/NuSMV/NuSMV-2.5.4/nusmv/src',
    './dependencies/NuSMV/NuSMV-2.5.4/cudd-2.4.1.1/include'
]

LIBRARIES = libraries_info()

# This is a list of generic arguments that need to be repeated over and over
# for each of the extensions we generate
EXTENSION_ARGS = {
  # The swig specific arguments
  'swig_opts'      : ['-py3'] + [ '-I{}'.format(inc) for inc in INCLUDES ],
  'include_dirs'   : INCLUDES,
  'extra_compile_args': ['-g', '-fPIC'],
  **LIBRARIES
}


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

# setup est vraiment l'endroit ou on va builder le module python et le packager
# le 'name' correspond au nom du module qui sera packaged et installé dans les libs
# le 'ext_modules' correspond aux modules d'extension (en C) qui sont nécessaires
#    au module qui va etre installe
# le 'py_modules' correspond aux modules python qui vont composer le corps du
#    module insallé.
setup(name             = 'pynusmv',
      version          = "1.0-RC01",
      author           = "Simon BUSARD, Xavier GILLARD",
      author_email     = "simon.busard@uclouvain.be, xavier.gillard@uclouvain.be",
      url              = "http://lvl.info.ucl.ac.be/Tools/PyNuSMV",
      description      = "Embed NuSMV as a python library",
      ext_modules      = EXTENSIONS,
      packages         = find_packages(),
      install_requires = ['pyparsing']
      )
