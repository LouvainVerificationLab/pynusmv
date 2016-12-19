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
  * This file contains the header for the lower interface of the
  * (custom) BMC module containing code initially written in Python and
  * then translated in C for performance reason: profiling revealed that
  * these function were real performance bottlenecks of the PyNuSMV BMC
  * addition.
  *************************************************************************/
#ifndef __PYNUSMV_BMC_LOWER_IFACE_H__
#define __PYNUSMV_BMC_LOWER_IFACE_H__

#include <stdlib.h>
#include <nusmv-config.h>
#include <utils/defs.h>

#include <bmc/bmc.h>

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
be_ptr proposition_at_time(BeEnc_ptr enc, node_ptr formula, int time);
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
int succ(int k, int l, int time);
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
be_ptr fairness_constraint(BeFsm_ptr fsm, int k, int l);
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
be_ptr loop_condition(BeEnc_ptr enc, int k, int l);
/*
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
be_ptr sem_no_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int offset);
/*
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
be_ptr sem_with_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int loop, int offset);

/* This function is the non memoized version of :see:`sem_no_loop_offset`.
 * All the arguments and return value keep the same meaning between the two functions.
 *
 * .. note:: This is the place where the heavy lifting is done.
 */
be_ptr NO_MEMOIZE_sem_no_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int offset);
/* This function is the non memoized version of :see:`sem_with_loop_offset`.
 * All the arguments and return value keep the same meaning between the two functions.
 *
 * .. note:: This is the place where the heavy lifting is done.
 */
be_ptr NO_MEMOIZE_sem_with_loop_offset(BeFsm_ptr fsm, node_ptr formula, int time, int bound, int loop, int offset);

/* ********** FILE DOCUMENTATION ******************************************/

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
node_ptr MEMOIZER_key(node_ptr formula, int time, int k, int l, int offset);
/* Retrieves a memoized value identified by `key` (:see: `MEMOIZER_key`)
 *
 * :param key: the key to use to retrieve the memoized value.
 * :return: the memoized value associated with `key` or NULL if none was found.
 */
be_ptr MEMOIZER_get(node_ptr key);
/* Associates a memoized value `be` identified by `key` (:see: `MEMOIZER_key`).
 *
 * :param key: the key to use to store the memoized value.
 * :param be: the value to store and associate to `key`
 */
void MEMOIZER_put(node_ptr key, be_ptr be);
/* Clears the memoization cache and reclaims all its associated system resources.
 *
 * .. warning::
 *    This function *MUST* be called whenever the BMC sub system is deinitialized in PyNuSMV.
 */
void MEMOIZER_clear();

#endif
