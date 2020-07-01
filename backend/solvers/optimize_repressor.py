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
    Generates a graph for the passed in function in the same style as the log
    based graphs in the assignment.

    Args:
        func: The function to graph.
        start: At what point to start the graph
        stop: At what point to stop the graph.
        number_of_observations: Number of observations to plot. Given the
            curvature of the sigmoidal functions, a very high observation
            count is recommended, or you will end up with angular graphs.
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
        bio_optimization: str = 'DNA'
):
    '''
    Monolithic entrypoint and wrapper around the optimization functionality
    of Scipy.

    I will freely admit my ignorance on the benefits and drawbacks of many of
    these optimization algorithms.

    Args:
        input_repressor: The input to optimize.
        optimization_method:
        bio_optimization:

    Returns:

    '''
    if bio_optimization == 'DNA':
        curried_optimize = partial(
            optimizable_response_function_dna,
            input_repressor=input_repressor,
        )
        variable_count = 2
    if bio_optimization == 'ALL':
        curried_optimize = partial(
            optimizable_response_function_dna_and_protein,
            input_repressor=input_repressor,
        )
        variable_count = 4
    # Scipy Global optimization methods have a different interface than
    # the standard minimize.
    if optimization_method in [
        'dual_annealing',
        'basin-hopping',
        'differential-evolution',
        'shgo',
        'brute',
    ]:
        bounds_list = []
        # I assume that practically messing with the ymin and ymax of a
        # repressor has some sort of bound, but it's not detailed in the
        # assignment. If you look at the UCF the maximum y max is 6.8, so lets
        # call it ten?
        bounds_list.append([0.0, 10.0])
        # Same with K bounds, going for something higher than what is seen
        # in the standard e-coli UCF.
        bounds_list.append([0, 0.5])
        if bio_optimization == 'ALL':
            # Stretching can be 0:1.5
            bounds_list.append([0, 1.5])
            bounds_list.append([0, 1.05])
        # Avg Run Time: 6000ms
        if optimization_method == 'dual_annealing':
            return opt.dual_annealing(
                curried_optimize,
                bounds=bounds_list,
            )
        # Avg Run Time: 4800ms
        if optimization_method == 'basin-hopping':
            return opt.basinhopping(
                curried_optimize,
                [1] * variable_count
            )
        # Avg Run Time: 195ms
        if optimization_method == 'differential-evolution':
            return opt.differential_evolution(
                curried_optimize,
                bounds=bounds_list,
            )
        # Avg Run Time: 9ms, but fails to actually converge to anything useful.
        # Upon casual research into the field of optimization, it's probably
        # my initial conditions.
        if optimization_method == 'shgo':
            return opt.shgo(
                curried_optimize,
                bounds=bounds_list,
            )
        # Avg Run Time: 76ms.
        if optimization_method == 'brute':
            return opt.brute(
                curried_optimize,
                ranges=bounds_list,
            )
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
        return opt.minimize(
            curried_optimize,
            [1] * variable_count,
            method=optimization_method,
        )
    else:
        raise RuntimeError(
            f'Unable to find requested optimization method '
            f'{optimization_method}'
        )


def optimizable_response_function_dna(x, input_repressor: Repressor) -> float:
    '''
    Alters the linear coefficents that determine the score of a repressor and
    returns the new value. Used for optimization.

    Args:
        x: x0, x1 corresponding to changes in [ymin, ymax] and k respectively.
        input_repressor: Repressor to optimize.

    Returns:
        The score of the change repressor.
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


def optimizable_response_function_dna_and_protein(
        x,
        input_repressor: Repressor
) -> float:
    '''
    Alters the linear coefficents that determine the score of a repressor and
    returns the new value. Used for optimization.

    Args:
        x: x0, x1 corresponding to changes in [ymin, ymax] and k respectively.
        input_repressor: Repressor to optimize.

    Returns:
        The score of the change repressor.
    '''
    # First variable corresponds to changing y_min and y_max
    # Second variable corresponds to altering the RBS
    # Third variable corresponds to stretching the sigmoid
    # Fourth variable corresponds to changing the slope
    x0, x1, x2, x3, = x
    input_repressor = copy.deepcopy(input_repressor)
    # DNA
    input_repressor.y_min = input_repressor.y_min * x0
    input_repressor.y_max = input_repressor.y_max * x0
    input_repressor.k = input_repressor.k * x1
    # Protein
    input_repressor.y_max = input_repressor.y_max * x2
    input_repressor.y_min = input_repressor.y_min / x2
    input_repressor.n = input_repressor.n * x3
    # The negative sign is so we minimize a negative value, so we end up
    # maximizing the function.
    return -input_repressor.score_self()



def simple_calculate_response_function(x, coefficients: list) -> float:
    '''
    Simple response function calculation for value of x. Designed to be 
    used in tandem with 'get_linear_coefficents' method of Repressor Gates.

    Args:
        x: Input signal value.
        coefficients: Linear coefficients. (ymin, ymax, k, n)

    Returns:
        The response function of the repressor.

    '''
    y_min, y_max, k, n = map(np.float64, coefficients)
    return y_min + ((y_max - y_min) / (1.0 + (x / k) ** n))
