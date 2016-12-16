%module(package="pynusmv.nusmv.compile.type_checking.checkers") checkers

%include ../../../global.i

%{
#include "../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/compile/type_checking/checkers/CheckerBase.h" 
#include "../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/compile/type_checking/checkers/CheckerCore.h" 
#include "../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/compile/type_checking/checkers/CheckerPsl.h" 
#include "../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/compile/type_checking/checkers/CheckerStatement.h" 
%}

%feature("autodoc", 1);

%include ../../../typedefs.tpl

%include ../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/compile/type_checking/checkers/CheckerBase.h
%include ../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/compile/type_checking/checkers/CheckerCore.h
%include ../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/compile/type_checking/checkers/CheckerPsl.h
%include ../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/compile/type_checking/checkers/CheckerStatement.h