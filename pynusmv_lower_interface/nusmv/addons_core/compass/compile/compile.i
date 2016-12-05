%module(package="pynusmv.nusmv.addons_core.compass.compile") compile

%include ../../../global.i

%{
#include "../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/addons_core/compass/compile/ProbAssign.h" 
%}

%feature("autodoc", 1);

%include ../../../typedefs.tpl

%include ../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/addons_core/compass/compile/ProbAssign.h