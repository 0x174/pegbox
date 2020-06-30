from typing import Callable
from functools import partial

import numpy as np
from scipy import optimize as opt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from backend.datastructures import Repressor

def graph_response_function(
        func: Callable,
        start: int = 0.001,
        stop: int = 1000,
        number_of_observations: int = 1000000,
):
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


def optimizable_response_function_dna(x, coefficents):
    '''

    Args:
        x:
        y_min:
        y_max:
        k:
        n:

    Returns:

    '''
    x0, x1 = x
    y_min, y_max, k, n = coefficents
    new_y_min = y_min * x0
    new_y_max = y_max * x0
    print(new_y_min)
    print(new_y_max)
    divisor = (new_y_max - (new_y_max / 2.0))
    dividend = new_y_min * (2.0 - new_y_min)
    x = (k * x1) * n ** (1.0 / (divisor / dividend))
    lowest_on = (x / (new_y_max / 2))
    highest_off = x / (new_y_min * 2)
    # TODO: You need to realize this function better. Needs the boolean
    #  inputs and outputs
    return (np.log(lowest_on / highest_off))


def response_function_dna(x, coefficents):
    '''

    Args:
        x:
        coefficents:

    Returns:

    '''
    y_min, y_max, k, n = map(np.float64, coefficents)
    return y_min + ((y_max - y_min) / (1.0 + (x / k) ** n))


if __name__ == '__main__':
    s1 = Repressor(
        y_max=3.8,
        y_min=0.06,
        k=1.0,
        n=1.6,
        number_of_inputs=1,
    )
    s1.set_biological_inputs([0.0013, 0])
    curried_optimize = partial(optimizable_response_function_dna, coefficents=s1.get_linear_coefficents())
    results = opt.minimize(
        curried_optimize,
        [15, 1],
    )
    if results.success:
        fitted_params = results.x
    curried_abstract = partial(
        response_function_dna,
        coefficents=s1.get_linear_coefficents()
    )
    graph_response_function(curried_abstract)
