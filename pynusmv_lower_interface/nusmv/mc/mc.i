%module(package="pynusmv.nusmv.mc") mc

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/mc/mc.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/mc/mcInt.h"
%}

// Ignoring unimplemented functions
%ignore check_invariant_forward;

%feature("autodoc", 1);

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/mc/mc.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/mc/mcInt.h