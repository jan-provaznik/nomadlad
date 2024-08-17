import nomadlad
import numpy as np

def blackbox_01 (point_list):
    '''
    Optimal solution is 0 for point = 1.
    '''

    for point in point_list:
        diffs = point - 1.0
        value = np.sum(diffs ** 2)
        yield 1, 1, f'{value:.16f}'

def test_blackbox_01 ():
    parameters = [
            'BB_OUTPUT_TYPE OBJ',
            'BB_MAX_BLOCK_SIZE 10',
            'MAX_BB_EVAL 100',
            'DIMENSION 1',
            'DIRECTION_TYPE ORTHO 2N',
            'SEED 1337',
            'X0          ( 2.0 )',
            'LOWER_BOUND ( 0.0 )',
            'UPPER_BOUND ( 5.0 )',
            'DISPLAY_DEGREE 0'
    ]

    solution = nomadlad.minimize(blackbox_01, parameters, multiple = False)
    solution_point = solution[3][1]
    assert np.isclose(solution_point, 1.0)

    solution = nomadlad.minimize(blackbox_01, parameters, multiple = True)
    assert 29 == len(solution[3])

    solution_point = solution[3][0][1]
    assert np.isclose(solution_point, 1.0)

def blackbox_02 (point_list):
    '''
    There are two optimal solutions. 
    Two distinct points, -1 and +1, give the optimal 0.
    '''

    for point in point_list:
        diffs = (point ** 2) - 1.0
        value = np.sum(diffs ** 2)
        yield 1, 1, f'{value:.16f}'

def test_blackbox_02 ():
    parameters = [
            'BB_OUTPUT_TYPE OBJ',
            'BB_MAX_BLOCK_SIZE 10',
            'MAX_BB_EVAL 100',
            'DIMENSION 1',
            'DIRECTION_TYPE ORTHO 2N',
            'SEED 1337',
            'X0          (  0.0 )',
            'LOWER_BOUND ( -5.0 )',
            'UPPER_BOUND (  5.0 )',
            'DISPLAY_DEGREE 0'
    ]

    # The particular choice of X0 and SEED should result in the first solution
    # being the -1 point.

    solution = nomadlad.minimize(blackbox_02, parameters, multiple = False)
    solution_point = solution[3][1]
    assert np.isclose(solution_point, -1.0)

    # There should be 35 solutions reported.
    # The first one is -1, the last one is +1.

    solution = nomadlad.minimize(blackbox_02, parameters, True)
    assert 35 == len(solution[3])

    solution_point = solution[3][0][1]
    assert np.isclose(solution_point, -1.0)

    solution_point = solution[3][-1][1]
    assert np.isclose(solution_point, +1.0)

