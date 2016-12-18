/* ********** COPYRIGHT DISCLAIMER ***************************************
 * This file is part of PyNuSMV + bmc.
 *
 * PyNuSMV + bmc is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * PyNuSMV + bmc is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with PyNuSMV + bmc.  If not, see <http://www.gnu.org/licenses/>.
 *************************************************************************/

 /* ********** FILE DOCUMENTATION *****************************************
  * This file contains the implementation of the lower interface of the
  * (custom) BMC module containing code initially written in Python and
  * then translated in C for performance reason: profiling revealed that
  * these function were real performance bottlenecks of the PyNuSMV BMC
  * addition.
  *************************************************************************/
#include "lower_intf.h"

#include <stdlib.h>

#include <parser/symbols.h>
#include <node/node.h>
#include <be/be.h>
#include <fsm/be/BeFsm.h>

#include <enc/enc.h>
#include <compile/compile.h>

#include <bmc/bmcConv.h>


/****** REAL STUFF COMPUTATION ********************************************************************
 * BEWARE, these functions are not memoized (but these are the ones that actually DO PERFORM
 * the heavy lifting). If your need to give a look at the memoized versions of these functions,
 * they are declared at the very end of this file.
 **************************************************************************************************/

 /*
  * This function shifts the formula (not necessarily booleanized) encoded
  * in the given `formula` node up until the moment where it is timed at
  * `time`.
  *
  * .. note::
  *    Albeit initially written in python, profiling revealed that the
  *    implementation of this function in pure python was a terrible performance
  *    killer. Therefore it was translated in this C function.
  *
  * .. note::
  *    In python, this function has the same meaning as::
  *
  *        expr = Wff.decorate(formula).to_boolean_wff().to_be(enc)
  *        return enc.shift_to_time(expr, offset+time)
  *
  * :param enc: the BeEnc (pointer) to use to shift the formula.
  * :param formula: the node encoding the formula to shift to some given time stamp.
  * :param time: the logical time block at which to shift `formula`.
  * :return: a boolean expression corresponding to `formula` at `time`
  */
be_ptr proposition_at_time(BeEnc_ptr enc, node_ptr formula, int time){
  BddEnc_ptr bddenc = Enc_get_bdd_encoding();
  Expr_ptr   bexpr  = Compile_detexpr2bexpr(bddenc, formula);
  be_ptr     expr   = Bmc_Conv_Bexp2Be(enc, (node_ptr) bexpr);

  return BeEnc_untimed_expr_to_timed(enc, expr, time);
}

/*
 * Returns the successor time of `time` in the context of a (loopy) trace
 * (k-l loop) on the interval [loop; bound].
 *
 * .. note::
 *     This function was initially written in python and was ported back to C
 *     only for the sake of convenience when developing the other APIS.
 *
 * .. warning::
 *     The error checking and consistency verification *MUST* be done in the
 *     python code calling this function.
 *
 * .. note::
 *     In the particular case where the value of `l` equal to `no_loopback()`,
 *     then the sucessor is simply `time` + 1. If on top of that, `time` is
 *     equal to `k`. Then there is no sucessor and the value None is returned.
 *
 * .. note::
 *     References, see Definition 6
 *     in Biere et al - ``Bounded Model Checking'' - 2003
 *
 * .. warning::
 *     To be consistent with the way the loop condition is implemented (equiv
 *     of all the state variables). In the case of a loopy path (k-l loop)
 *     we have that walking 'k' steps means to be back at step 'l'. Hence, the
 *     value of i can only vary from 0 to k-1 (and will repeat itself in the
 *     range [l; k-1])
 *
 * :param time: the time whose successor needs to be computed.
 * :param k: the highest time
 * :param l: the time where the loop is assumed to start
 * :return: the successor of `time` in the context of a k-l loop.
 */
int succ(int k, int l, int time){
  return time < k -1 ? time + 1 : l;
}

/*
 * Computes a step of the constraint to be added to the loop side of the BE
 * when one wants to take fairness into account for the case where we consider
 * the existence of a k-l loop (between k and l obviously).
 *
 * .. note::
 *    Albeit initially written in python, profiling revealed that the
 *    implementation of this function in pure python was a terrible performance
 *    killer. Therefore it was translated in this C function.
 *
 * .. warning::
 *    The error checking and consistency verification *MUST* be done in the
 *    python code calling this function.
 *
 * .. note::
 *
 *     This code was first implemented in Python with PyNuSMV but, since
 *     the Python implementation proved to be a huge performance bottleneck
 *     (profiling revealed that useless memory management was dragging the
 *     whole system behind), it has been translated back to C to deliver much
 *     better perf. results.
 *
 * :param fsm: the fsm whose transition relation must be unrolled
 * :param k: the maximum (horizon/bound) time of the problem
 * :param l: the time where the loop starts
 * :return: a step of the fairness constraint to force fair execution on the
 *     k-l loop.
 */
be_ptr fairness_constraint(BeFsm_ptr fsm, int k, int l){
  BeEnc_ptr      enc     = BeFsm_get_be_encoding(fsm);
  Be_Manager_ptr manager = BeEnc_get_be_manager(enc);

  if (Bmc_Utils_IsNoLoopback(l)){
    return Be_Falsity(manager);
  }

  be_ptr constraint = Be_Truth(manager);
  if (k == 0){
    return constraint;
  }

  node_ptr iter = BeFsm_get_fairness_list(fsm);
  while(iter != NULL){
    be_ptr fairness = (be_ptr) car(iter);
    be_ptr expr     = BeEnc_untimed_to_timed_or_interval(enc, fairness, l, k-1);
    constraint      = Be_And(manager, constraint, expr);
    /* next */
    iter = cdr(iter);
  }

  return constraint;
}

/*
 * This function generates a Be expression representing the loop condition
 * which is necessary to determine that k->l is a backloop.
 *
 * Formally, the returned constraint is denoted _{l}L_{k}
 *
 * Because the transition relation is encoded in Nusmv as formula (and not as
 * a relation per-se), we determine the existence of a backloop between
 * l < k and forall var, var(i) == var(k)
 *
 * That is to say: if it is possible to encounter two times the same state
 * (same state being all variables have the same value in both states) we know
 * there is a backloop on the path
 *
 * .. note::
 *    Albeit initially written in python, profiling revealed that the
 *    implementation of this function in pure python was a terrible performance
 *    killer. Therefore it was translated in this C function.
 *
 * .. warning::
 *    The error checking and consistency verification *MUST* be done in the
 *    python code calling this function.
 *
 * .. note::
 *
 *     This code was first implemented in Python with PyNuSMV but, since
 *     the Python implementation proved to be a huge performance bottleneck
 *     (profiling revealed that useless memory management was dragging the
 *     whole system behind), it has been translated back to C to deliver much
 *     better perf. results.
 *
 * :param fsm: the fsm on which the condition will be evaluated
 * :param k: the highest time
 * :param l: the time where the loop is assumed to start
 * :return: a Be expression representing the loop condition that verifies that
 *     k-l is a loop path.
 */
be_ptr loop_condition(BeEnc_ptr enc, int k, int l){
  int iter = BeEnc_get_first_untimed_var_index(enc, BE_VAR_TYPE_CURR);

  Be_Manager_ptr manager = BeEnc_get_be_manager(enc);
  be_ptr cond = Be_Truth(manager);

  while (BeEnc_is_var_index_valid(enc, iter)) {
    be_ptr vl = BeEnc_index_to_timed(enc, iter, l);
    be_ptr vk = BeEnc_index_to_timed(enc, iter, k);
    cond = Be_And(manager, cond, Be_Iff(manager, vl, vk));
    iter = BeEnc_get_next_var_index(enc, iter, BE_VAR_TYPE_CURR);
  }

  return cond;
}

/* *********** THIS FUNCTION IS NOT MEMOIZED BUT DOES THE HEAVY LIFTING *********************
 * Generates the Be [[formula]]^{time}_{bound} corresponding to the bounded semantic
 * of `formula` when there is no loop on the path but encodes it with an `offset` long shift
 * in the timeline of the encoder.
 *
 * .. note::
 *
 *     This code was first implemented in Python with PyNuSMV but, since
 *     the Python implementation proved to be a huge performance bottleneck
 *     (profiling revealed that useless memory management was dragging the
 *     whole system behind), it has been translated back to C to deliver much
 *     better perf. results.
 *
 * .. warning::
 *    The error checking and consistency verification *MUST* be done in the
 *    python code calling this function.
 *
 * .. note::
 *
 *     This function plays the same role as `bounded_semantics_without_loop` but allows to
 *     position the time blocks at some place we like in the encoder timeline. This is mostly
 *     helpful if you want to devise verification methods that need to have multiple parallel
 *     verifications. (ie. diagnosability).
 *
 *     Note however, that the two implementations are different.
 *
 * .. warning::
 *
 *     So far, the only supported temporal operators are F, G, U, R, X
 *
 * :param fsm: the BeFsm for which the property will be verified. Actually, it is only used to
 *     provide the encoder used to assign the variables to some time blocks. The api was kept
 *     this ways to keep uniformity with its non-offsetted counterpart.
 * :param formula: the property for which to generate a verification problem
 *     represented in a 'node' format (subclass of :see::class:`pynusmv.node.Node`)
 *     which corresponds to the format obtained from the ast. (remark: if you
 *     need to manipulate [ie negate] the formula before passing it, it is
 *     perfectly valid to pass a node decorated by `Wff.decorate`).
 * :param time: the logical time at which the semantics is to be evaluated. (Leave out the offset for
 *     this param. If you intend the 3rd state of a trace, say time 2).
 * :param bound: the logical time bound to the problem. (Leave out the offset for this param: if you
 *     intend to have a problem with at most 10 steps, say bound=10)
 * :param offset: the time offset in the encoding block where the sem of this formula will be
 *     generated.
 * :return: a Be corresponding to the semantics of `formula` at `time` for a problem with a maximum
 *     of `bound` steps encoded to start at time `offset` in the `fsm` encoding timeline.
 */
be_ptr NO_MEMOIZE_sem_no_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int offset){
  BeEnc_ptr      enc     = BeFsm_get_be_encoding(fsm);
  Be_Manager_ptr manager = BeEnc_get_be_manager(enc);

  if(time > bound){
    return Be_Falsity(manager);
  }
  switch(node_get_type(formula)){
  case AND:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr right= sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    return Be_And(manager, left, right);
    }
  case OR:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr right= sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    return Be_Or(manager, left, right);
    }
  case XOR:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr right= sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    return Be_Xor(manager, left, right);
    }
  case NOT:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    return Be_Not(manager, left);
    }
  case IMPLIES:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr right= sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    return Be_Implies(manager, left, right);
    }
  case IFF:
    {
    be_ptr left = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr right= sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    return Be_Iff(manager, left, right);
    }
  case OP_NEXT:
    return sem_no_loop_offset(fsm, car(formula), time+1, bound, offset);
  case OP_GLOBAL:
    return Be_Falsity(manager);
  case OP_FUTURE:
    {
    be_ptr now = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr then= sem_no_loop_offset(fsm, formula, time+1, bound, offset);
    return Be_Or(manager, now, then);
    }
  case UNTIL:
    {
    be_ptr psi = sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    be_ptr phi = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr then= sem_no_loop_offset(fsm, formula, time+1, bound, offset);
    return Be_Or(manager, psi, Be_And(manager, phi, then));
    }
  case RELEASES:
    {
    be_ptr psi = sem_no_loop_offset(fsm, cdr(formula), time, bound, offset);
    be_ptr phi = sem_no_loop_offset(fsm, car(formula), time, bound, offset);
    be_ptr then= sem_no_loop_offset(fsm, formula, time+1, bound, offset);
    return Be_And(manager, psi, Be_Or(manager, phi, then));
    }
  default:
    {
    return proposition_at_time(enc, formula, time + offset);
    }
  }
  /* never reached */
  return NULL;
}

/* *********** THIS FUNCTION IS NOT MEMOIZED BUT DOES THE HEAVY LIFTING *********************
 * Generates the Be _{loop}[[formula]]^{time}_{bound} corresponding to the bounded semantic
 * of `formula` when a loop starts at time 'loop' on the path but encodes it with an `offset`
 * long shift in the timeline of the encoder.
 *
 * .. note::
 *
 *     This code was first implemented in Python with PyNuSMV but, since
 *     the Python implementation proved to be a huge performance bottleneck
 *     (profiling revealed that useless memory management was dragging the
 *     whole system behind), it has been translated back to C to deliver much
 *     better perf. results.
 *
 * .. warning::
 *    The error checking and consistency verification *MUST* be done in the
 *    python code calling this function.
 *
 * .. note::
 *
 *     This function plays the same role as `bounded_semantics_with_loop` but allows to
 *     position the time blocks at some place we like in the encoder timeline. This is mostly
 *     helpful if you want to devise verification methods that need to have multiple parallel
 *     verifications. (ie. diagnosability).
 *
 *     Note however, that the two implementations are different.
 *
 * .. warning::
 *
 *     So far, the only supported temporal operators are F, G, U, R, X
 *
 * :param fsm: the BeFsm for which the property will be verified. Actually, it is only used to
 *     provide the encoder used to assign the variables to some time blocks. The api was kept
 *     this ways to keep uniformity with its non-offsetted counterpart.
 * :param formula: the property for which to generate a verification problem
 *     represented in a 'node' format (subclass of :see::class:`pynusmv.node.Node`)
 *     which corresponds to the format obtained from the ast. (remark: if you
 *     need to manipulate [ie negate] the formula before passing it, it is
 *     perfectly valid to pass a node decorated by `Wff.decorate`).
 * :param time: the logical time at which the semantics is to be evaluated. (Leave out the offset for
 *     this param. If you intend the 3rd state of a trace, say time 2).
 * :param bound: the logical time bound to the problem. (Leave out the offset for this param: if you
 *     intend to have a problem with at most 10 steps, say bound=10)
 * :param loop: the logical time at which a loop starts on the path. (Leave out the offset for this
 *     param. If you intend to mean that loop starts at 2nd state of the trace, say loop=2)
 * :param offset: the time offset in the encoding block where the sem of this formula will be
 *     generated.
 * :return: a Be corresponding to the semantics of `formula` at `time` for a problem with a maximum
 *     of `bound` steps encoded to start at time `offset` in the `fsm` encoding timeline.
 */
be_ptr NO_MEMOIZE_sem_with_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int loop, int offset){
  BeEnc_ptr      enc     = BeFsm_get_be_encoding(fsm);
  Be_Manager_ptr manager = BeEnc_get_be_manager(enc);

  if(bound == 0){
    return Be_Falsity(manager);
  }
  if(time > bound){
    return Be_Falsity(manager);
  }
  switch(node_get_type(formula)){
  case AND:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    be_ptr right= sem_with_loop_offset(fsm, cdr(formula), time, bound, loop, offset);
    return Be_And(manager, left, right);
    }
  case OR:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    be_ptr right= sem_with_loop_offset(fsm, cdr(formula), time, bound, loop, offset);
    return Be_Or(manager, left, right);
    }
  case XOR:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    be_ptr right= sem_with_loop_offset(fsm, cdr(formula), time, bound, loop, offset);
    return Be_Xor(manager, left, right);
    }
  case NOT:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    return Be_Not(manager, left);
    }
  case IMPLIES:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    be_ptr right= sem_with_loop_offset(fsm, cdr(formula), time, bound, loop, offset);
    return Be_Implies(manager, left, right);
    }
  case IFF:
    {
    be_ptr left = sem_with_loop_offset(fsm, car(formula), time, bound, loop, offset);
    be_ptr right= sem_with_loop_offset(fsm, cdr(formula), time, bound, loop, offset);
    return Be_Iff(manager, left, right);
    }
  case OP_NEXT:
    return sem_with_loop_offset(fsm, car(formula), succ(bound, loop, time), bound, loop, offset);
  case OP_GLOBAL:
    {
      int i;
      be_ptr result = Be_Truth(manager);
      for(i = min(time, loop); i<bound; i++){
        result = Be_And(manager, result, sem_with_loop_offset(fsm, car(formula), i, bound, loop, offset));
      }
      return result;
    }
  case OP_FUTURE:
    {
      int i;
      be_ptr result = Be_Falsity(manager);
      for(i = min(time, loop); i<bound; i++){
        result = Be_Or(manager, result, sem_with_loop_offset(fsm, car(formula), i, bound, loop, offset));
      }
      return result;
    }
  case UNTIL:
    {
      int i;
      be_ptr result = Be_Falsity(manager);
      /* Go reverse ! */
      for(i = bound-1; i>=min(time, loop); i--){
          be_ptr psi    = sem_with_loop_offset(fsm, cdr(formula), i, bound, loop, offset);
          be_ptr phi    = sem_with_loop_offset(fsm, car(formula), i, bound, loop, offset);
          result        = Be_Or(manager, psi, Be_And(manager, phi, result));
      }
      return result;
    }
  case RELEASES:
    {
      /* NOTE: This operator is just a slight bit more complex than the others.
       *
       * Indeed, the initial result is set to PSI because having G psi is enough
       * to satisfy [ phi R psi ]. Hence, the last moment in the loop cannot be
       * just encoded as ( psi & ( phi | true ) ) because, at that time and in
       * that context, we just don't care about the value of phi.
       *
       * Therefore, we loop backwards on all the possible moments of the loopy
       * path and enforce the last moment to be PSI only.
       */
      int i;
      be_ptr result = sem_with_loop_offset(fsm, cdr(formula), bound-1, bound, loop, offset);
      /* Go reverse ! */
      for(i = bound-2; i>=min(time, loop); i--){
          be_ptr psi    = sem_with_loop_offset(fsm, cdr(formula), i, bound, loop, offset);
          be_ptr phi    = sem_with_loop_offset(fsm, car(formula), i, bound, loop, offset);
          result        = Be_And(manager, psi, Be_Or(manager, phi, result));
      }
      return result;
    }
  default:
    {
    return proposition_at_time(enc, formula, time + offset);
    }
  }
  /* never reached */
  return NULL;
}

/****** MEMOIZATION *******************************************************************************
 * These functions do not do anything on their own, they only serve the purpose of caching the
 * results of some of the functions declared above.
 **************************************************************************************************/

/* This function just memoizes the result of `NO_MEMOIZE_sem_no_loop_offset` (see above) */
be_ptr sem_no_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int offset){
  node_ptr key    = MEMOIZER_key(formula, time, bound, Bmc_Utils_GetNoLoopback(), offset);
  be_ptr   result = MEMOIZER_get(key);

  if (result == (be_ptr) NULL){
    result = NO_MEMOIZE_sem_no_loop_offset(fsm, formula, time, bound, offset);
    MEMOIZER_put(key, result);
  }

  return result;
}

/* This function just memoizes the result of `NO_MEMOIZE_sem_with_loop_offset` (see above) */
be_ptr sem_with_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int loop, int offset){
  node_ptr key    = MEMOIZER_key(formula, time, bound, loop, offset);
  be_ptr   result = MEMOIZER_get(key);

  if (result == (be_ptr) NULL){
    result = NO_MEMOIZE_sem_with_loop_offset(fsm, formula, time, bound, loop, offset);
    MEMOIZER_put(key, result);
  }

  return result;
}

/****** MEMOIZATION *******************************************************************************
 * Memoization related functions
 **************************************************************************************************/

/* This is the private cache where all the memoized values are stored */
static hash_ptr MEMOIZER = (hash_ptr) NULL;

/* This function is used to compute an unique key to retrieve the some memoized value for
 * computed for `formula` at time `time` on a path bounded by k-l. (Note: for a straight
 * path, the value of `l` is expected to be NuSMV NO_LOOP constant).
 *
 * :param k: the logical time bound to the problem. (Leave out the offset for this param: if you
 *     intend to have a problem with at most 10 steps, say bound=10)
 * :param l: the logical time at which a loop starts on the path. (Leave out the offset for this
 *     param. If you intend to mean that loop starts at 2nd state of the trace, say loop=2)
 * :param offset: the time offset in the encoding block where the sem of this formula will be
 *     generated.
 * :return: a key to retrive the memoized result of the computation that was made.
 */
node_ptr MEMOIZER_key(node_ptr formula, int time, int k, int l, int offset) {

  return find_node(CONS, formula,
                   find_node(CONS, PTR_FROM_INT(node_ptr, time),
                             find_node(CONS, PTR_FROM_INT(node_ptr, k),
                            		 find_node(CONS, PTR_FROM_INT(node_ptr, l),
                            				         PTR_FROM_INT(node_ptr, offset)
									 )
                              )
					)
		 );
}

/* Retrieves a memoized value identified by `key` (:see: `MEMOIZER_key`)
 *
 * :param key: the key to use to retrieve the memoized value.
 * :return: the memoized value associated with `key` or NULL if none was found.
 */
be_ptr MEMOIZER_get(node_ptr key){
  if (MEMOIZER == (hash_ptr) NULL) {
    MEMOIZER = new_assoc();
  }
  return (be_ptr) find_assoc(MEMOIZER, key);
}

/* Associates a memoized value `be` identified by `key` (:see: `MEMOIZER_key`).
 *
 * :param key: the key to use to store the memoized value.
 * :param be: the value to store and associate to `key`
 */
void MEMOIZER_put(node_ptr key, be_ptr be){
  if (MEMOIZER == (hash_ptr) NULL) {
    MEMOIZER = new_assoc();
  }
  insert_assoc(MEMOIZER, key, (node_ptr) be);
}

/* Clears the memoization cache and reclaims all its associated system resources.
 *
 * .. warning::
 *    This function *MUST* be called whenever the BMC sub system is deinitialized in PyNuSMV.
 */
void MEMOIZER_clear(){
  if (MEMOIZER != (hash_ptr) NULL) {
    free_assoc(MEMOIZER);
    MEMOIZER = (hash_ptr) NULL;
  }
}
