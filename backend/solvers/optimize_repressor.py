import copy
from typing import Callable
from functools import partial

import numpy as np
from scipy import optimize as opt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from backend.datastructures import Repressor


# ------------------------ Publicly Available Functions ------------------------
def graph_response_function(
        func: Callable,
        start: int = 0.001,
        stop: int = 1000,
        number_of_observations: int = 1000000,
):
    '''

    Args:
        func:
        start:
        stop:
        number_of_observations:

    Returns:

    '''
    x = np.linspace(start, stop, number_of_observations)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlim([.001, 1000])
    ax.set_ylim([.001, 1000])
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.3f'))
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.3f'))
    plt.plot(x, list(map(func, x)))
    plt.show()


def optimize_repressor(
        input_repressor: Repressor,
        optimization_method: str,
):
    '''

    Args:
        input_repressor:
        optimization_method:
        display:

    Returns:

    '''
    curried_optimize = partial(
        optimizable_response_function_dna,
        input_repressor=input_repressor,
    )
    # Scipy Global optimization methods have a different interface than
    # the standard minimize.
    if optimization_method in [
        'dual_annealing',
        'basin-hopping',
        'differential-evolution',
        'shgo',
        'brute',
    ]:
        # I assume that practically messing with the ymin and ymax of a
        # repressor has some sort of bound, but it's not detailed in the
        # assignment. If you look at the UCF the maximum y max is 6.8, so lets
        # call it ten?
        y_bounds = [0.0, 10.0]
        # Same with K bounds, going for something higher than what is seen
        # in the standard e-coli UCF.
        k_bounds = [0, 0.5]
        import time
        start_time = time.time()
        # Avg Run Time: 6000ms
        if optimization_method == 'dual_annealing':
            thing = opt.dual_annealing(
                curried_optimize,
                bounds=[y_bounds, k_bounds],
            )
            print(time.time() - start_time)
            return thing
        # Avg Run Time: 4800ms
        if optimization_method == 'basin-hopping':
            thing = opt.basinhopping(
                curried_optimize,
                [1, 1]
            )
            print(time.time() - start_time)
            return thing
        # Avg Run Time: 195ms
        if optimization_method == 'differential-evolution':
            thing = opt.differential_evolution(
                curried_optimize,
                bounds=[y_bounds, k_bounds],
            )
            print(time.time() - start_time)
            return thing
        # Avg Run Time: 9ms, but fails to actually converge to anything useful.
        # Upon casual research into the field of optimization, it's probably
        # my initial conditions.
        if optimization_method == 'shgo':
            thing = opt.shgo(
                curried_optimize,
                bounds=[y_bounds, k_bounds],
            )
            print(time.time() - start_time)
            return thing
        # Avg Run Time: 76ms.
        if optimization_method == 'brute':
            thing = opt.brute(
                curried_optimize,
                ranges=(y_bounds, k_bounds),
            )
            print(time.time() - start_time)
            return thing
    elif optimization_method in [
        'Nelder-Mead',
        'Powell',
        'CG',
        'BFGS',
        'Newton-CG',
        'L-BFGS-B',
        'TNC',
        'COBYLA',
        'SLSQP',
        'trust-constr',
        'dogleg',
        'trust-ncg',
        'trust-krylov',
        'trust-exact',
    ]:
        import time
        start_time = time.time()
        thing = opt.minimize(
            curried_optimize,
            [0, 1],
            method=optimization_method,
        )
        print(time.time() - start_time)
        return thing


def optimizable_response_function_dna(x, input_repressor: Repressor):
    '''

    Args:
        x
        input_repressor

    Returns:

    '''
    # First variable corresponds to changing y_min and y_max
    # Second variable corresponds to altering the RBS
    x0, x1 = x
    input_repressor = copy.deepcopy(input_repressor)
    input_repressor.y_min = input_repressor.y_min * x0
    input_repressor.y_max = input_repressor.y_max * x0
    input_repressor.k = input_repressor.k * x1
    # The negative sign is so we minimize a negative value, so we end up
    # maximizing the function.
    return -input_repressor.score_self()


def calculate_response_function(x, coefficents):
    '''

    Args:
        x:
        coefficents:

    Returns:

    '''
    y_min, y_max, k, n = map(np.float64, coefficents)
    return y_min + ((y_max - y_min) / (1.0 + (x / k) ** n))
