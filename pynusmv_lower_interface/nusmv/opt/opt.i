%module(package="pynusmv.nusmv.opt") opt

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/opt/opt.h" 
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/opt/OptsHandler.h" 
%}

// Ignoring unimplemented functions
%ignore opt_use_ltl_tableau_reachable_states;
%ignore set_use_ltl_tableau_reachable_states;
%ignore unset_use_ltl_tableau_reachable_states;

%feature("autodoc", 1);

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/opt/opt.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/opt/OptsHandler.h