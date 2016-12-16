%module(package="pynusmv.nusmv.node.normalizers") normalizers

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/normalizers/MasterNormalizer.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/normalizers/NormalizerBase.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/normalizers/NormalizerCore.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/normalizers/NormalizerPsl.h" 
%}

// Ignoring unimplemented functions
%ignore MasterNormalizer_destroy;

%feature("autodoc", 1);

%include ../../typedefs.tpl

%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/object.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/normalizers/MasterNormalizer.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/normalizers/NormalizerBase.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/normalizers/NormalizerCore.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/node/normalizers/NormalizerPsl.h