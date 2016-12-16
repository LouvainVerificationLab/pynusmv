%module(package="pynusmv.nusmv.be") be

%include ../global.i

%{
#include <stdio.h>
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/be/be.h" 
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/be/bePkg.h" 
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/be/beRbcManager.h" 
%}

%feature("autodoc", 1);

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/be/be.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/be/bePkg.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/be/beRbcManager.h
