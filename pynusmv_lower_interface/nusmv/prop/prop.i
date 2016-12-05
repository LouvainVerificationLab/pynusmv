%module(package="pynusmv.nusmv.prop") prop

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/prop/Prop.h" 
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/prop/PropDb.h" 
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/prop/propPkg.h" 
%}

%feature("autodoc", 1);

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/prop/Prop.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/prop/PropDb.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/prop/propPkg.h