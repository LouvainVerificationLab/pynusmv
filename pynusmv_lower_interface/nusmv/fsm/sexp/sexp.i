%module(package="pynusmv.nusmv.fsm.sexp") sexp

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/sexp/BoolSexpFsm.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/sexp/Expr.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/sexp/sexp.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/sexp/SexpFsm.h"
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/sexp/BoolSexpFsm.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/sexp/Expr.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/sexp/sexp.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/sexp/SexpFsm.h

%inline %{

SexpFsm_ptr boolsexpfsm_to_sexpfsm(BoolSexpFsm_ptr ptr){
    return (SexpFsm_ptr) ptr;
}

%}
