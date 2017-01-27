%module(package="pynusmv.nusmv.ltl") ltl

%include ../global.i

%{
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/nusmv-config.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h"
#include "../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/ltl/ltl.h"
%}

%feature("autodoc", 1);

%inline %{

struct Ltl_StructCheckLtlSpec_TAG {
    Prop_ptr prop; /* The property to verify */
    BddFsm_ptr fsm; /* The FSM representing the product model and
                       tableau */
    BddEnc_ptr bdd_enc; /* The BDD encoder */
    DdManager *dd;  /* The BDD package manager */
    SymbTable_ptr symb_table; /* The Symbol Table */
    SymbLayer_ptr tableau_layer; /* The layer where tableau variables
                                    will be added */
    bdd_ptr s0; /* The BDD representing the result of the verification */
    node_ptr spec_formula;
    Ltl_StructCheckLtlSpec_oreg2smv oreg2smv; /* The tableau constructor
                                                 to use. This one may
                                                 generate additional
                                                 LTL, that will be
                                                 removed by ltl2smv */
    Ltl_StructCheckLtlSpec_ltl2smv ltl2smv;   /* The tableau constructor
                                                 to use. This is used to
                                                 remove additional LTL
                                                 properties left by
                                                 oreg2smv */
    boolean negate_formula; /* flag to keep track wether the formula has
                               to be negated or not */
    boolean removed_layer; /* Flag to inform wether the layer has been
                              removed or not */
    boolean do_rewriting; /* Enables the rewriting to remove input from
                             properties */
};

%}

%inline %{

EXTERN node_ptr
witness ARGS((BddFsm_ptr fsm, BddEnc_ptr enc, bdd_ptr feasible));

%}

%include ../typedefs.tpl

%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/utils/defs.h
%include ../../../dependencies/NuSMV/NuSMV-2.5.4/nusmv/src/ltl/ltl.h
