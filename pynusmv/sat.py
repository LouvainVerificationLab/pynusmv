"""
The :mod:`pynusmv.sat` module contains classes and functions related to the 
operation and manipulation of the different sat solvers available in PyNuSMV.
"""
from pynusmv_lower_interface.nusmv.utils import utils as _utils
from pynusmv_lower_interface.nusmv.sat   import sat   as _sat
from enum                import IntEnum
from pynusmv             import utils
from pynusmv.collections import Slist, IntConversion
from pynusmv.utils       import writeonly
from pynusmv_lower_interface.nusmv.utils.utils import int_to_void_star


class SatSolverResult(IntEnum):
    """
    This result represents the possible outcomes of a sat solving. 
    """
    INTERNAL_ERROR        = _sat.SAT_SOLVER_INTERNAL_ERROR
    TIMEOUT               = _sat.SAT_SOLVER_TIMEOUT
    MEMOUT                = _sat.SAT_SOLVER_MEMOUT
    SATISFIABLE           = _sat.SAT_SOLVER_SATISFIABLE_PROBLEM
    UNSATISFIABLE         = _sat.SAT_SOLVER_UNSATISFIABLE_PROBLEM 
    UNAVAILABLE           = _sat.SAT_SOLVER_UNAVAILABLE
    
class Polarity(IntEnum):
    """
    In general, a polarity is assigned to a formula and its variables. If this
    were not done, this would potentially slow down the solver because the 
    solver would unnecessarily try to assign values to many variables.
    """
    POSITIVE =  1
    NEGATIVE = -1
    NOT_SET  =  0
        
class SatSolverFactory():
    # =========================================================================
    # ========== Utility functions ============================================
    # =========================================================================
    @staticmethod
    def normalize_name(name):
        """
        :return: a normalized solver name corresponding to the given `name`.
          (Only case should be changed)
        :param name: the name (string) of the solver to normalize.
        :raise: ValueError whenever the name corresponds to none of the 
          available solvers
        """
        normalized = _sat.Sat_NormalizeSatSolverName(name)
        if normalized is None:
            raise ValueError("No such SAT solver available : {}".format(name))
        else:
            return normalized

    @staticmethod
    def available_solvers():
        """
        :return: a list with the name of the solvers that can be instantiated
        """
        return set(_sat.Sat_GetAvailableSolversString().split())
    
    @staticmethod 
    def print_available_solvers(stdio_file=utils.StdioFile.stdout()):
        """
        prints the list of available SAT solvers to the given stdio file 
        """
        _sat.Sat_PrintAvailableSolvers(stdio_file.handle)
        
    @staticmethod
    def create(name='MiniSat', incremental=True, proof=True):
        """
        Creates a new sat solver corresponding to the given name and capabilities
        :param name: the name of the solver to instanciate 
        :param incremental: a flag indicating whether the instanciated solver
        should have incremental capabilities
        :param proof: a flag indicating whether the instanciated solver should
        have proof logging capability.
        :return: a new sat solver corresponding to the given name and capabilities
        
        :raise: Given that ZChaff does not support proof logging, this method
          raises a ValueError when prooflogging is turned on and zchaff is passed
          as name parameter.
        """
        if SatSolverFactory.normalize_name(name) == 'ZChaff' and proof:
            raise ValueError("""
                Proof logging not supported when using the zchaff  SAT Solver. 
                Please retry using MiniSat
                """)
        
        if incremental:
            if proof:
                return SatIncProofSolver(
                                _sat.Sat_CreateIncProofSolver(name))
            else:
                return SatIncSolver(_sat.Sat_CreateIncSolver(name))
        else:
            if proof:
                return SatProofSolver(
                                _sat.Sat_CreateNonIncProofSolver(name))
            else:
                return SatSolver(
                                _sat.Sat_CreateNonIncSolver(name))
        raise Exception("Could not create solver")
        
class SatSolver(utils.PointerWrapper):
    """
    This class encapsulates the capabilities any sat solver should provide
    """
    def __init__(self, ptr, freeit=True):
        """
        Creates a new sat solver from 'ptr'
        :param ptr: a 'raw' NuSMV pointer to an instantiated solver 
        :type  ptr: A SatSolver_ptr
        """
        assert(ptr is not None)
        super().__init__(ptr, freeit=freeit)
        
    def _free(self):
        """
        Overrides utils.PointerWrapper._free, the method in charge of 
        deallocating any resource related to this object
        """
        if self._freeit and self._ptr is not None:
            _sat.SatSolver_destroy(self._as_SatSolver_ptr())
            self._freeit = False
            self._ptr    = None
            
    def _as_SatSolver_ptr(self):
        """
        :return: the pointer of this object casted to the SatSolver_ptr type
        """
        return self._ptr
    
    # =========================================================================
    # ============== General info =============================================
    # =========================================================================
    @property
    def name(self):
        """:return: the name of the instanciated solver"""
        return _sat.SatSolver_get_name(self._as_SatSolver_ptr())
    
    @property
    def last_solving_time(self):
        """:return: the time of the last solving"""
        return _sat.SatSolver_get_last_solving_time(self._as_SatSolver_ptr())
    
    @property
    def permanent_group(self):
        """
        :return: the permanent group of this class instance
        
        Every solver has one permanent group that can not be destroyed.
        This group may has more efficient representation and during invocations
        of any 'solve' functions, the permanent group will always be
        included into the groups to be solved.
        """
        return _sat.SatSolver_get_permanent_group(self._as_SatSolver_ptr())
    
    @writeonly
    def random_mode(self, seed):
        """
        Enables or disables random mode for polarity. (useful to perform sat 
        based simulation)
        
        If given seed is != 0, then random polarity mode is enabled
        with given seed, otherwise random mode is disabled.
        
        :param seed: a double serving to initialize the PRNG or zero to disable
          random mode
        """
        _sat.SatSolver_set_random_mode(self._as_SatSolver_ptr(), seed)
    
    # =========================================================================
    # ============== Solving proper ===========================================
    # =========================================================================
    def add(self, cnf):
        """
        Adds a CNF formula to the set of CNF to be solved (more specifically to
        the permanent group of this solver).
        
        The function does not specify the polarity of the formula.
        This should be done using the polarity function of this solver.
        In general, if polarity is not set any value can be assigned to the formula
        and its variables  (this may potentially slow down the solver because
        there is a number of variables whose value can be any and solver will try to
        assign values to them though it is not necessary). Moreover, some solver
        (such as ZChaff) can deal with non-redundant clauses only, so the input
        clauses must be non-redundant: no variable can be in the same clause twice.
        CNF formula may be a constant.
        
        :param cnf: a BeCnf representing a boolean expression encoded in CNF
        """
        group_ptr = _sat.SatSolver_get_permanent_group(self._as_SatSolver_ptr())
        _sat.SatSolver_add(self._as_SatSolver_ptr(), cnf._ptr, group_ptr)
    
    def __iadd__(self, cnf):
        """
        Adds syntax sugar to post cnf clauses to the solver's permanent group
        
        :param cnf: the cnf clause to add to the solver's permanent group
        """
        self.add(cnf)
        return self
    
    def polarity(self, be_cnf, polarity, group=None):
        """
        sets the polarity mode of the solver for the given group and formula
        
        :param be_cnf: a BeCnf formula whose polarity in the group is to be set
        :param polarity: the new polarity
        :param group: the group on which the polarity applies
        """
        grp= self.permanent_group if group is None else group
        me = self._as_SatSolver_ptr()
        _sat.SatSolver_set_polarity(me, be_cnf._ptr, polarity, grp)
    
    def solve(self):
        """
        Tries to solve all the clauses of the (permanent group of the) solver and
        returns the flag.
        
        :return: the outcome of the solving (value in SatSolverResult)
        """
        # Note: an optional 'assumptions' parameter was initially foreseen to 
        # call SatSolver_solve_all_groups_assume(...) but it turns out that this
        # api always triggers segfaults when called (it tries to free 'conflict'
        # which is NULL.
        return SatSolverResult(_sat.SatSolver_solve_all_groups(self._as_SatSolver_ptr()))
    
    @property
    def model(self):
        """
        Returns a list of values in dimacs form that satisfy the set of formulas
         
        The previous solving call should have returned SATISFIABLE.
        The returned list is a list of values in dimac form (positive literal
        is included as the variable index, negative literal as the negative
        variable index, if a literal has not been set its value is not included).
        
        :return: a list of values in dimac form that satisfy the set of formulas
        """
        lst = _sat.SatSolver_get_model(self._as_SatSolver_ptr())
        return Slist(lst, IntConversion(), freeit=False)
    
    def __repr__(self):
        """
        :return: a string representation of this solver (mostly usefule for
            debugging purpose
        """
        return self.__class__.__name__+" ( "+self.name+" )"

################################################################################
# Provokes a SEGFAULT whenever called.
################################################################################       
#     @property
#     def conflicts(self):
#         """
#         Returns the set of conflicting assumptions.
#         
#         .. note::
#         
#           - At the time being, the use of this function is only allowed on 
#             instances of MiniSat 
#           - This function should be used only after solve or solve_all_groups 
#             with a set of assumptions different from None
#           - More information about inc. solving under assumption:
#               PHD Thesis:
#               Sörensson, N. (2008). Effective SAT solving. 
#               Department of Computer Science and Engineering
#               University of GOTHENBURG, Sweden.
#               
#           
#         :return: an Slist of int which represent the indices of the conflict
#            literals in the CNF being sat solved. 
#         """
#         # this functionality is only available for SatMiniSAT
#         assert(self.name == 'MiniSat')
#         lst = _sat.SatSolver_get_conflicts(self._as_SatSolver_ptr())
#         return Slist(lst, IntConversion())

################################################################################
# NEVER USED IN NUSMV, hence not exposed
################################################################################  
#     @property
#     def polarity_mode(self):
#         """:return: the current polarity mode of this solver"""
#         return _sat.SatSolver_get_polarity_mode(self._as_SatSolver_ptr())
#      
#     @polarity_mode.setter
#     def polarity_mode(self, polarity):
#         """
#         sets the polarity mode of the solver
#         :param polarity: the new polarity
#         """
#         _sat.SatSolver_set_polarity_mode(self._as_SatSolver_ptr(), polarity)
################################################################################           
#     @writeonly
#     def preferred_variables(self, cnfvar_slist):
#         """
#         Sets preferred variables in the solver. 
#         
#         A preferred variable is split upon with priority, with respect to 
#         non-preferedd ones.
#         
#         :param cnfvar_slist: an slist containing the CNF variables which will 
#           be considered the preferred variables
#         """
#         _sat.SatSolver_set_preferred_variables(self._as_SatSolver_ptr(), cnfvar_slist._ptr)
#     
#     def clear_preferred_variables(self):
#         """Removes any preferred variable config from the solver""" 
#         _sat.SatSolver_clear_preferred_variables(self._as_SatSolver_ptr())
#
################################################################################
# NOT DOCUMENTED, hence not exposed
################################################################################        
#     @indexed.getter
#     def cnf_variable(self, var):
#         """
#         :return: the index of the cnf variable corresponding to the given 
#           internal variable 
#         """ 
#         return _sat.SatSolver_get_cnf_var(self._as_SatSolver_ptr(), var)
################################################################################

class SatIncSolver(SatSolver):
    """
    This class encapsulates the capabilities of an incremental sat solver (ie: 
    manipulate groups)
    """
    def __init__(self, ptr, freeit=True):
        """
        Creates a new instance of an incremental sat solver from the given `ptr`
        
        :param ptr: the pointer to wrap in this object
        :param freeit: a flag indicating whether or not the system resources
          associated with this object should be reclaimed upon garbage collect.
        """  
        super().__init__(ptr, freeit=freeit)
        
    def _free(self):
        """Frees the system resources of this object if necessary"""
        if self._freeit and self._ptr is not None:
            # Actually, this boils down to SatSolver_destroy which itself 
            # reduces to object->finalize(self)
            _sat.SatIncSolver_destroy(self._ptr)
            self._freeit = False
            self._ptr    = None
        
    def _as_SatSolver_ptr(self):
        """:return: a hook to the underlying pointer caster as SatSolver_ptr""" 
        me = self._as_SatIncSolver_ptr()
        return _sat.SatIncSolver_cast_to_SatSolver_ptr(me)
    
    def _as_SatIncSolver_ptr(self):
        """
        :return: a hook to the underlying pointer caster as SatIncSolver_ptr
        """
        return self._ptr
    
    def create_group(self):
        """
        Creates a new group and returns its ID
        
        :return: the id of the newly created group
        """
        return _sat.SatIncSolver_create_group(self._as_SatIncSolver_ptr())
    
    def destroy_group(self, group):
        """
        Destroy an existing group and all formulas in it. 
        :param group: the group to destroy
        :raise: ValueError if the given group is the solver's permanent group
        """
        if group == self.permanent_group:
            raise ValueError("Permanent group cannot be destroyed")
        _sat.SatIncSolver_destroy_group(self._as_SatIncSolver_ptr(), group)
    
    def move_to_permanent(self, group):
        """
        Moves all formulas from a group into the permanent group of
        the solver and then destroy the given group. Permanent group may have 
        more efficient implementation, but cannot be destroyed
        
        :param group: the group whose formulas are to be moved to the permanent
          group. 
        """
        # NOTE: this is never used in NuSMV
        me = self._as_SatIncSolver_ptr()
        _sat.SatIncSolver_move_to_permanent_and_destroy_group(me, group)
        
    def add_to_group(self, cnf, group):
        """
        Adds a CNF formula to a group 
        
        The function does not specify the polarity of the formula.
        This should be done using the set_group_polarity function of this solver.
        In general, if polarity is not set any value can be assigned to the formula
        and its variables  (this may potentially slow down the solver because
        there is a number of variables whose value can be any and solver will try to
        assign values to them though it is not necessary). Moreover, some solver
        (such as ZChaff) can deal with non-redundant clauses only, so the input
        clauses must be non-redundant: no variable can be in the same clause twice.
        CNF formula may be a constant.
        
        :param cnf: a BeCnf representing a boolean expression encoded in CNF
        :param group: the solving group to which add the cnf formula
        """
        me = self._as_SatSolver_ptr()
        _sat.SatSolver_add(me, cnf._ptr, group)
        
    def solve_groups(self, groups):
        """
        Tries to solve formulas from the groups in the list.
        
        .. note::
            - The permanent group is automatically added to the list.
            - the model property may be accessed iff this function returns
              SatSolverResult.SATISFIABLE
              
        :return: a flag whether the solving was successful.
        """
        me   = self._as_SatIncSolver_ptr()
        olist= _utils.Olist_create()
        for g in groups:
            _utils.Olist_append(olist, int_to_void_star(g))
            
        result = _sat.SatIncSolver_solve_groups(me, olist)
        _utils.Olist_destroy(olist)
        return SatSolverResult(result)
    
    def solve_without_groups(self, groups):
        """
        Tries to solve formulas in groups belonging to the solver except the 
        groups in the given list `groups_olist`

        .. note::
            - The permanent group may not be in the groups_olist
            - the model property may be accessed iff this function returns
              SatSolverResult.SATISFIABLE
              
        :return: a flag whether the solving was successful.
        """
        
        if self.permanent_group in groups:
            raise ValueError("The permanent group may be in the groups_olist")
        
        me   = self._as_SatIncSolver_ptr()
        olist= _utils.Olist_create()
        for g in groups:
            _utils.Olist_append(olist, int_to_void_star(g))
            
        result = _sat.SatIncSolver_solve_without_groups(me, olist)
        _utils.Olist_destroy(olist)
        return SatSolverResult(result)
    
    def solve_all_groups(self):
        """
        Solves all groups belonging to the solver and returns the flag
        
        :return: the outcome of the solving (value in SatSolverResult)
        """
        # Note: an optional 'assumptions' parameter was initially foreseen to 
        # call SatSolver_solve_all_groups_assume(...) but it turns out that this
        # api always triggers segfaults when called (it tries to free 'conflict'
        # which is NULL.
        return self.solve()

###############################################################################
# Not documented in the C code, so not exposed !         
###############################################################################         
#     @property
#     def curr_itp_group(self):
#         # FIXME : not documented ...
#         return _sat.SatSolver_curr_itp_group(self._as_SatSolver_ptr())
#     
#     def new_itp_group(self):
#         # FIXME : not documented ...
#         return _sat.SatSolver_new_itp_group(self._as_SatSolver_ptr())
###############################################################################
    
class SatIncProofSolver(SatIncSolver):
    """
    This type is simply a 'marker' type meant to show that this kind of solver
    has both incremental sat solving and proof logging capability.
    """
    def __init__(self, ptr, freeit=True):
        super().__init__(ptr, freeit=freeit)

class SatProofSolver(SatSolver):
    """
    This type is simply a 'marker' type meant to show that this kind of solver
    has proof logging capability.
    """
    def __init__(self, ptr, freeit=True):
        super().__init__(ptr, freeit=freeit)
    