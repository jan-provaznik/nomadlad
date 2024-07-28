import numpy
import nomadlad

import functools
import mpi4py.futures

# Blackbox function. 
#
# Given a single numpy.ndarray point to evaluate the blackbox at.
# Returns (success, include, outcome) triplet.
#
# Value of 'outcome' must follow the 'BB_OUTPUT_TYPE' option!

def blackbox (point):
    fw = numpy.linalg.norm(point - 1, 2)
    cw = 2 - numpy.linalg.norm(point, 2)

    success = 1
    include = 1
    outcome = '{:.16f} {:.16f}'.format(fw, cw)

    return success, include, outcome

# Parameters for the NOMAD optimization engine.
# Note BB_MAX_BLOCK_SIZE, BB_OUTPUT_TYPE and MAX_BB_EVAL options.
    
parameters = [
    'BB_OUTPUT_TYPE OBJ PB',
    'BB_MAX_BLOCK_SIZE 10',
    'MAX_BB_EVAL 1000',

    'SEED {}'.format(numpy.random.randint(0, 64)),
    'ADD_SEED_TO_FILE_NAMES no',

    'DIMENSION 2',
    "DIRECTION_TYPE ORTHO 2N",

    'X0          ( 2.0  2.0 )',
    'LOWER_BOUND ( 0.0  0.0 )',
    'UPPER_BOUND ( 5.0  5.0 )',

    'DISPLAY_DEGREE 0',

    # 'DISPLAY_DEGREE 2',
    # 'DISPLAY_STATS (BBE BLK_SIZE) [OBJ] (SOL) BBO',
]

# :)

def program ():

    # The concurrent.futures.ProcessPoolExecutor and 
    # mpi4py.futures.MPIPoolExecutor classes share a common interface,
    # the map function.
    #
    # This makes the transition from local to alocal parallelism easier.

    with mpi4py.futures.MPIPoolExecutor() as executor:
        # Construct the parallel evaluator
        evaluator = functools.partial(executor.map, blackbox)

        # Perform the optimization ritual.
        result = nomadlad.minimize(evaluator, parameters) 

    # Unpack and print out its result
    flag, status, eval_count, best_feasible, best_infeasible = result

    print('final termination flag           ', flag)
    print('final termination status         ', status)
    print('blackbox evaluation count        ', eval_count)
    print('best   feasible result (f(w), w) ', best_feasible)
    print('best infeasible result (f(w), w) ', best_infeasible)

if __name__ == '__main__':
    program()

