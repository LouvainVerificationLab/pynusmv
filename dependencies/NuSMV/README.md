# NuSMV
The source code enclosed in the NuSMV-2.5.4.tar.gz archive was directly downloaded from
the foundation Bruno Kessler. http://nusmv.fbk.eu

The NuSMV software is licensed to you under the terms of the Lesser GPL
(see https://www.gnu.org/licenses/lgpl-3.0.en.html).

## Patches
In order to blend NuSMV with our framework, avoid useless rewrite of existing and realize some of
our experiments, the following files have been patched. There are extremely few changes, and these
have been marked explicitly as such. Here is the list:
  * nusmv/src/bmc/sbmc/sbmcTableauIncLTLformula.c
      - sbmc_unroll_invariant_f() : the `static` modifier was removed so as to expose the function.
      - sbmc_unroll_invariant_p() : the `static` modifier was removed so as to expose the function.
  * nusmv/src/cmd/cmdMisc.c
      - an assertion was commented out to allow init-quit cycles.
  *  nusmv/src/parser/symbols.h
      - symbols AW and EW were added (this was part of an experiment).
  * nusmv/src/parser/psl/pslExpr.h
      - commented out the `PSL_EXPR_MAKE_W_N2W_OP` which was defined twice.
  * nusmv/src/prop/Prop.h
      - commented out the declaration of `Prop_set_name` which is later redefined with const keyword.
  * The makefiles of CUDD have also been patched so as to compile the source code of that lib with `-fPIC` flag which allows the embedding of its code in a shared object.
These patches are automatically applied at build time via the use of the makefiles. You can consult
the details of these patches directly from the content of the `*.patch` files. These are regular
diffs obtained through the use of the UNIX `diff -u` command.
