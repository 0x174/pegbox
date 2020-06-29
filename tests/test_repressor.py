import pytest

from backend import (
    Repressor,
    InputSignal,
)


@pytest.fixture
def generate_s1_gate():
    '''
    Generates an S1 Repressor as detailed in assignment.

    Returns:
        A Repressor Object with the

    '''
    return Repressor(
        y_max=1.3,
        y_min=0.003,
        k=0.01,
        n=2.9,
        number_of_inputs=1,
    )


@pytest.fixture
def generate_p1_gate():
    '''
    Generates an S1 Repressor as detailed in assignment.

    Returns:
        A Repressor Object with the

    '''
    return Repressor(
        y_max=3.9,
        y_min=0.01,
        k=0.03,
        n=4,
        number_of_inputs=2,
    )


@pytest.fixture
def generate_plux_star():
    lux = InputSignal(
        label='pLuxStar',
        off_value=0.025,
        on_value=0.31,
    )
    lux.set_binary_value(0b0011)
    return lux


@pytest.fixture
def generate_ptet():
    ptet = InputSignal(
        label='pTet',
        off_value=0.0013,
        on_value=4.4,
    )
    ptet.set_binary_value(0b0101)
    return ptet


def test_logic_functions(generate_s1_gate):
    s1 = generate_s1_gate
    # Singular input testing.
    s1.set_logical_inputs([0b0101])
    s1.set_logical_function('NOT')
    assert s1.get_logical_output() == 0b1010
    # Multiple input testing
    s1.set_logical_function('AND')
    s1.set_logical_inputs([0b0000, 0b1111])
    assert s1.get_logical_output() == 0b0000

    s1.set_logical_function('OR')
    s1.set_logical_inputs([0b0000, 0b1111])
    assert s1.get_logical_output() == 0b1111

    s1.set_logical_function('XOR')
    s1.set_logical_inputs([0b1010, 0b0101])
    assert s1.get_logical_output() == 0b1111

    s1.set_logical_function('NAND')
    s1.set_logical_inputs([0b1100, 0b0011])
    assert s1.get_logical_output() == 0b1111

    s1.set_logical_function('NOR')
    s1.set_logical_inputs([0b1100, 0b0011])
    assert s1.get_logical_output() == 0b0000

    s1.set_logical_function('XNOR')
    s1.set_logical_inputs([0b1010, 0b1010])
    assert s1.get_logical_output() == 0b1111


def test_gate_instantiation(generate_s1_gate):
    '''

    Returns:

    '''
    s1 = generate_s1_gate
    assert s1 is not None


def test_response_function_calculation(generate_s1_gate, generate_ptet):
    '''

    Args:
        generate_S1_repressor:

    Returns:

    '''
    s1 = generate_s1_gate
    ptet = generate_ptet
    s1.set_biological_inputs([ptet])
    assert s1.calculate_response_function([0b0101]) == \
           pytest.approx(1.2965149647184224, 0.1)


def test_logic_gate_setting(generate_s1_gate):
    s1 = generate_s1_gate
    s1.set_logical_function('NOT')
    s1.set_logical_inputs([0b0101])
    assert s1.get_logical_output() == 0b1010


def test_connected_gates(generate_s1_gate, generate_p1_gate):
    '''

    Returns:

    '''
    s1 = generate_s1_gate
    s1.set_biological_inputs([0.0013, 4.4])
    s1.set_logical_function('NOT')
    s1.set_logical_inputs([0b0101])
    p1 = generate_p1_gate
    p1.set_biological_inputs([0.0025, s1])
    p1.set_logical_inputs([0b0011, s1])
    p1.set_logical_function('NOR')
    assert p1.get_logical_output() == 0b100
    assert p1.calculate_response_function([0b0011]) == 0.01000110656742123


def test_circuit_score(generate_s1_gate, generate_p1_gate, generate_plux_star, generate_ptet):
    s1 = generate_s1_gate
    p1 = generate_p1_gate
    plux = generate_plux_star
    ptet = generate_ptet
    s1.set_biological_inputs([ptet])
    p1.set_biological_inputs([plux, s1])
    s1.score_self()
