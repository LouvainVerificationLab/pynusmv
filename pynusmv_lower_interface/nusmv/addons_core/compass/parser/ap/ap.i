%module(package="pynusmv.nusmv.addons_core.compass.parser.ap") ap

%include ../../../../global.i

%{
#include "../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/node.h"
#include "../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/addons_core/compass/parser/ap/ap_grammar.h" 
#include "../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/addons_core/compass/parser/ap/ParserAp.h" 
%}

// Removing warnings for redefined macros (TOK_X defined twice in ap_grammar)
#pragma SWIG nowarn=302

%feature("autodoc", 1);

%include ../../../../typedefs.tpl

%include ../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/addons_core/compass/parser/ap/ap_grammar.h
%include ../../../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/addons_core/compass/parser/ap/ParserAp.h