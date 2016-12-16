%module(package="pynusmv.nusmv.fsm") fsm

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/fsm.h" 
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/FsmBuilder.h" 
%}

%feature("autodoc", 1);

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/fsm.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/FsmBuilder.h