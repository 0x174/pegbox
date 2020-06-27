import numpy as np
from scipy import optimize as opt
from backend.datastructures import Repressor


def abstract_response_function_dna(x, coefficents):
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
    x, y_min, y_max, k, n = coefficents
    new_y_min = y_min * x0
    new_y_max = y_max * x0
    divisor = (new_y_max - (new_y_max / 2.0))
    dividend = new_y_min * (2.0 - new_y_min)
    x = (k * x1) * n ** (1.0 / (divisor / dividend))
    lowest_on = (x / (new_y_max / 2))
    highest_off = x / (new_y_min * 2)
    return (np.log(lowest_on / highest_off))


if __name__ == '__main__':
    s1 = Repressor(
        y_max=1.3,
        y_min=0.003,
        k=0.01,
        n=2.9,
        number_of_inputs=1,
    )
    s1.set_chemical_inputs(0.0013, 0)
    # print(s1.get_coefficents())
    results = opt.minimize(
        fun=abstract_response_function_dna,
        x0=np.random.rand(2),
        args=s1.get_coefficents(),
        options={'disp': True},
    )
    print(results)
