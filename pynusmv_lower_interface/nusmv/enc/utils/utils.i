%module(package="pynusmv.nusmv.enc.utils") utils

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/utils/AddArray.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/utils/OrdGroups.h" 
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/utils/AddArray.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/enc/utils/OrdGroups.h