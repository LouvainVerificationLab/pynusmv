%module(package="pynusmv.nusmv.enc") enc

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/enc.h" 
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/operators.h" 
%}

%feature("autodoc", 1);

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/enc.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/operators.h