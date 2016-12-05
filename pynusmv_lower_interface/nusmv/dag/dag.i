%module(package="pynusmv.nusmv.dag") dag

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/dag/dag.h" 
%}

// Setting cpperraswarn to avoid problems with dag.h:91 (#error directive)
#pragma SWIG cpperraswarn=1
// And ignoring CPP #error warning
#pragma SWIG nowarn=205

// Ignoring unimplemented functions
%ignore Dag_ManagerAllocWithParams;

%feature("autodoc", 1);

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/dag/dag.h