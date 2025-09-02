import nomadlad
import numpy as np
import functools
import concurrent.futures

def blackbox_single_point (point):
    '''
    Optimal solution is (2 - sqrt(2)) for point = [ sqrt(2), sqrt(2) ].
    '''

    fw = np.linalg.norm(point - 1, 2)
    cw = 2 - np.linalg.norm(point, 2)
    return 1, 1, f'{fw:.16f} {cw:.16f}'

def test_blackbox_parallel ():
    parameters = [
        'BB_OUTPUT_TYPE OBJ PB',
        'BB_MAX_BLOCK_SIZE 10',
        'MAX_BB_EVAL 500',
        'SEED 1337',
        'DIMENSION 2',
        'DIRECTION_TYPE ORTHO 2N',
        'X0          ( 2.0  2.0 )',
        'LOWER_BOUND ( 0.0  0.0 )',
        'UPPER_BOUND ( 5.0  5.0 )',
        'DISPLAY_DEGREE 0'
    ]

    with concurrent.futures.ProcessPoolExecutor(2) as executor:
        evaluator = functools.partial(executor.map, blackbox_single_point)
        solution = nomadlad.minimize(evaluator, parameters)

    solution_value = solution[3][0]
    solution_point = solution[3][1]

    assert np.isclose(solution_value, 2 - np.sqrt(2))
    assert np.all(np.isclose(solution_point, np.sqrt(2)))

