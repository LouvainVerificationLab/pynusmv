%module(package="pynusmv.nusmv.parser.ord") ord

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/node.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/ord/ord_grammar.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/ord/ParserOrd.h" 
%}

// Removing duplicate macros definition (TOK_X macros).
#pragma SWIG nowarn=302

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/ord/ord_grammar.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/parser/ord/ParserOrd.h