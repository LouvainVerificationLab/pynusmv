%module(package="pynusmv.nusmv.trace") trace

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/pkg_trace.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/Trace.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/TraceLabel.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/TraceManager.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/TraceOpt.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/TraceXml.h"
%}

// Ignoring unimplemented functions
%ignore TraceManager_create_evaluator;
%ignore TraceOpt_eval_defines;
%ignore TraceOpt_set_eval_defines;
%ignore TraceOpt_set_xml_reader_halts_on_undefined_symbols;
%ignore TraceOpt_set_xml_reader_halts_on_wrong_section;
%ignore TraceOpt_xml_reader_halts_on_undefined_symbols;
%ignore TraceOpt_xml_reader_halts_on_wrong_section;
%ignore TracePkg_execution_engine_from_string;
%ignore TraceUtils_complete_trace;
%ignore Trace_covers_language;
%ignore Trace_symbol_get_category;
%ignore Trace_symbol_is_assigned;

%feature("autodoc", 1);

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/pkg_trace.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/Trace.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/TraceLabel.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/TraceManager.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/TraceOpt.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/trace/TraceXml.h

%inline %{

/* because concat requires 'other' address */
Trace_ptr Trace_concatenate(Trace_ptr self, Trace_ptr other){
  return Trace_concat(self, &other);
}

/* a structure describing an assignment as stored in the steps */
typedef struct {
  node_ptr      symbol;
  node_ptr      value;
  boolean       success;
  TraceStepIter iter;
} assignment_t;

/* retrieves the content of a step */
assignment_t Trace_step_get_assignment(TraceStepIter step_iter){
  assignment_t result;
  result.iter = step_iter;
  result.success = Trace_step_iter_fetch(&result.iter, &result.symbol, &result.value);

  return result;
}
%}
