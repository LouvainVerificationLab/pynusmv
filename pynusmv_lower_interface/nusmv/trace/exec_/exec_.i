%module(package="pynusmv.nusmv.trace.exec_") exec_

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/BaseTraceExecutor.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/BDDCompleteTraceExecutor.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/BDDPartialTraceExecutor.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/CompleteTraceExecutor.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/PartialTraceExecutor.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/SATCompleteTraceExecutor.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/SATPartialTraceExecutor.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/traceExec.h"
%}

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/BaseTraceExecutor.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/BDDCompleteTraceExecutor.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/BDDPartialTraceExecutor.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/CompleteTraceExecutor.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/PartialTraceExecutor.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/SATCompleteTraceExecutor.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/SATPartialTraceExecutor.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/exec/traceExec.h

%inline %{

PartialTraceExecutor_ptr bddPartialTraceExecutor2partialTraceExecutor(
                                              BDDPartialTraceExecutor_ptr ptr) {
    return (PartialTraceExecutor_ptr) ptr;
}

CompleteTraceExecutor_ptr bddCompleteTraceExecutor2completeTraceExecutor(
                                             BDDCompleteTraceExecutor_ptr ptr) {
    return (CompleteTraceExecutor_ptr) ptr;
}

CompleteTraceExecutor_ptr SATCompleteTraceExecutor2completeTraceExecutor(SATCompleteTraceExecutor_ptr ptr){
  return (CompleteTraceExecutor_ptr) ptr;
}

PartialTraceExecutor_ptr SATPartialTraceExecutor2partialTraceExecutor(SATPartialTraceExecutor_ptr ptr){
  return (PartialTraceExecutor_ptr) ptr;
}

%}
