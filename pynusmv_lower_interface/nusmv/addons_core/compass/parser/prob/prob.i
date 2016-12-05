%module(package="pynusmv.nusmv.addons_core.compass.parser.prob") prob

%include ../../../../global.i

%{
#include "../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/addons_core/compass/parser/prob/ParserProb.h" 
#include "../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/addons_core/compass/parser/prob/prob_grammar.h" 
%}

// Removing warnings for redefined macros (TOK_X defined twice in prob_grammar)
#pragma SWIG nowarn=302

%feature("autodoc", 1);

%include ../../../../typedefs.tpl

%include ../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/addons_core/compass/parser/prob/ParserProb.h
%include ../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/addons_core/compass/parser/prob/prob_grammar.h