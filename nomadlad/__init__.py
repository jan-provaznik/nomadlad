#!/bin/env python3
#
# 2021 - 2024 Jan Provaznik (jan@provaznik.pro)
#
# Interface for NOMAD, the blackbox optimization software.

def minimize (evaluator, configuration):
    '''
    Find global minimum using NOMAD blackbox optimizer.

    Parameters
    ----------
    evaluator : callable
        The blackbox evaluator function. 

        It must accept a numpy.ndarray payload of points where the objective
        and constraint functions of the blackbox should be evaluated. 

        It must return a list of (success, include, outcome) triplets. 
        Their elements indicate whether the blackbox evaluation at a particular
        point was successful, whether the evaluation should be included in the
        optimization and the actual outcome of the evaluation. 

        (1) success must be boolean-convertible (bool, int),
        (2) include must be boolean-convertible (bool, int),
        (3) outcome must be string-convertible  (str).

        The outcome string must conform to the BB_OUTPUT_TYPE configuration
        directive.

    configuration : list of strings
        A list configuration directives to be passed to the optimizer. See
        NOMAD documentation for complete list.

        Notable parameters include X0, LOWER_BOUND, UPPER_BOUND,
        BB_OUTPUT_TYPE, BB_MAX_BLOCK_SIZE, and MAX_BB_EVAL.

    Returns
    -------
    Returns a quintuple with the result.

    (1) termination_success : bool
        determines the exit condition of the solver
    (2) termination_status : int
        determines the termination status of the solver, as reported by NOMAD,
        with possible values { -6, -5, -4, -3, -2, -1, 0, 1 }
    (3) eval_count : int
        determines the number of blackbox evaluations
    (4) best_feasible is either a (best_value, best_point) tuple or None if
        there was no feasible solution found
    (5) best_infeasible behaves like best_feasible
    '''

    from ._nomadlad_bridge import minimize as _minimize
    return _minimize(evaluator, configuration)

'''
Version of the NOMAD bridge library.
'''
from ._nomadlad_bridge import __version__

'''
Version of the NOMAD optimization library.
'''
from ._nomadlad_bridge import __nomad_version__

