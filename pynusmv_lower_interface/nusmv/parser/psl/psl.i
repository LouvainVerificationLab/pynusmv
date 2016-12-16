%module(package="pynusmv.nusmv.parser.psl") psl

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/node.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/psl/pslExpr.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/psl/pslNode.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/psl/psl_grammar.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/psl/psl_symbols.h"  
%}

// Removing duplicate macros definition (token macros).
#pragma SWIG nowarn=302

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/psl/pslExpr.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/psl/pslNode.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/psl/psl_grammar.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/psl/psl_symbols.h