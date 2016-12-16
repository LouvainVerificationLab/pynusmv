%module(package="pynusmv.nusmv.cinit") cinit

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/cinit/cinit.h" 
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/cudd-2.4.1.1/include/cudd.h"
%}

// Removing possible memory leak warning
// The use of FILE* pointers can lead to memory leak.
// Have to be used cautiously.
#pragma SWIG nowarn=454

// Ignoring unimplemented functions
%ignore NuSMVCore_set_init_fun;
%ignore NuSMVCore_set_quit_fun;
%ignore NuSMVCore_set_reset_init_fun;
%ignore NuSMVCore_set_reset_quit_fun;

%feature("autodoc", 1);

%include ../typedefs.tpl

%inline %{
EXTERN DdManager* dd_manager;
%}

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/cinit/cinit.h