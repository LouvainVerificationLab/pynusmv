%module(package="pynusmv.nusmv.fsm.bdd") bdd

%include ../../global.i

%{
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/bdd/bdd.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/bdd/BddFsm.h" 
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/bdd/FairnessList.h" 

// Needed for BddFsmCache_ptr definition
#include "../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/bdd/bddInt.h"
%}

// Ignoring unimplemented functions
%ignore BddFsm_get_fair_states_subset;

%feature("autodoc", 1);

%include ../../typedefs.tpl


// Needed to be able to modify a BddFsm, like changing its transition
%inline %{

typedef struct BddFsm_TAG
{
  /* private members */
  DdManager*  dd;
  SymbTable_ptr symb_table;
  BddEnc_ptr  enc;

  BddStates      init;

  BddInvarStates invar_states;
  BddInvarInputs invar_inputs;

  BddTrans_ptr trans;

  JusticeList_ptr    justice;
  CompassionList_ptr compassion;

  BddFsmCache_ptr cache;
} BddFsm;

%}


%inline %{

FairnessList_ptr justiceList2fairnessList(JusticeList_ptr l) {
    return (FairnessList_ptr) l;
}

%}


%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/bdd/bdd.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/bdd/BddFsm.h
%include ../../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/fsm/bdd/FairnessList.h