import numpy
import nomadlad

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

# Blackbox function evaluator.
#
# Given a list of numpy.ndarray points to evaluate the blackbox at.
# Returns an iterable over (success, include, outcome) triplets.

def evaluator (block):
    for point in block:
        yield blackbox(point)

# Parameters for the NOMAD optimization engine.
# Note BB_MAX_BLOCK_SIZE, BB_OUTPUT_TYPE and MAX_BB_EVAL options.
    
parameters = [
    'BB_OUTPUT_TYPE OBJ PB',
    'BB_MAX_BLOCK_SIZE 10',
    'MAX_BB_EVAL 100',

    'SEED 1000000000',
    #'SEED {}'.format(numpy.random.randint(0, 2 ** 31)),
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

