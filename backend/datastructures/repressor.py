"""
backend.datastructures.repressor

Class encapsulating all behavior of a repressor/gate.

W.R. Jackson 2020
"""
from dataclasses import dataclass
from enum import Enum
import itertools
from typing import (
    List,
    Tuple,
    Union,
)

import numpy as np
import pandas as pd


@dataclass
class InputSignal:
    '''
    Attributes:
        label: String label for the input signal.
        on_value: Value when signal is 'on'
        off_value: Value when signal is 'off'
        binary_value: The (4-bit?) binary value of the input signal.
    '''
    label: str
    on_value: float
    off_value: float
    binary_value: int = None

    def __len__(self):
        return 1

    def set_binary_value(self, binary_value: int):
        '''
        Sets the binary value of the input signal.

        Args:
            binary_value: The binary value to set the input signal to.
        '''
        self.binary_value = binary_value


class LogicFunction(Enum):
    '''
    Enumeration of all possible boolean logic functions.
    '''
    NOT = 0
    AND = 1
    OR = 2
    XOR = 3
    NAND = 4
    NOR = 5
    XNOR = 6
    INITIAL = 7


class Repressor:
    def __init__(
            self,
            n: float,
            k: float,
            y_min: float,
            y_max: float,
            number_of_inputs: int,
    ):
        '''
        
        Args:
            n: Slope of the sigmoidal curve that defines the response function
            k: The distance between zero to the mid-point of the max slope of
                the x-axis
            y_min: The minimum y value
            y_max: The maximum y value
        '''
        self.n: float = n
        self.k: float = k
        self.y_max: float = y_max
        self.y_min: float = y_min
        self.number_of_inputs: int = number_of_inputs

        # Attributes related to counting the number of 'edits' done to the
        # repressor.
        self.dna_edits: int = 0
        self.protein_edits: int = 0

        # Attributes related to the biological input/output of the Repressor.
        # Inputs can be represented by either a dataclass representing the high
        # and low signal inputs to the repressor, or another repressor. The
        # output signal of those repressors is calculated recursively.
        self.biological_inputs: List[Union[Repressor, Tuple[float, float]]] = []
        self.biological_output: int = 0

        # Attributes related to the logical input/output to the Repressor.
        self.logical_function: LogicFunction = LogicFunction.INITIAL
        self.logical_output: bool = None
        self.logical_inputs: [List[Union[int, Repressor]]] = None

    def calculate_response_function(self, logical_inputs: List[bool]) -> float:
        '''
        Calculates the response function of the repressor as per the equation
        on page 3 of the homework. The repressor calculation looks like:

                                ymax - ymin
                    y = ymin + -------------
                                1.0 + (x/K)ⁿ

        Definitions for the variables of this function can be found in the
        class attribute definition.

        Returns:
            The biological output of the circuit
        '''
        current_x = 0
        for index, input_signal in enumerate(self.biological_inputs):
            if type(input_signal) is Repressor:
                current_x += input_signal.calculate_response_function(
                    [logical_inputs[index]]
                )
            if type(input_signal) is float:
                current_x += input_signal
        self.biological_output = self.y_min + (
                (self.y_max - self.y_min) /
                (1.0 + (current_x / self.k) ** self.n)
        )
        return self.biological_output

    def set_biological_inputs(
            self,
            biological_inputs: List[
                Union[
                    Tuple[float, float],
                    'Repressor',
                    InputSignal
                ]],
    ):
        '''
        Sets the biological inputs to the repressor.

        Args:
            biological_inputs: A list of biological inputs to the repressor.

        '''
        if len(self.biological_inputs) + 1 > self.number_of_inputs:
            raise RuntimeError('Too many inputs into gate.')
        input_list = []
        for chemical_input in biological_inputs:
            if type(chemical_input) == Tuple:
                input_list.append(InputSignal(
                    label='N/A',  # Possibly bad form. I think you'd have a db
                    # backing this in production that would probably have all
                    # signals predefined.
                    off_value=chemical_input[0],
                    on_value=chemical_input[1],
                ))
            if type(chemical_input) == Repressor or \
                    type(chemical_input) == InputSignal:
                input_list.append(chemical_input)
        self.biological_inputs.extend(biological_inputs)

    def set_logical_inputs(
            self,
            logical_inputs: List[Union[int, 'Repressor']],
    ):
        '''
        Sets the logical inputs to the repressor. This can either be via a
        adding another repressor where the logical output of that repressor
        will be calculated when called or setting a binary integer value.
        Binary values are prefixed with `0b****` for the purpose of conveying
        easily readable boolean gate logic.

        Args:
            logical_inputs: A list of logical inputs to the repressor.

        '''
        self.logical_inputs = logical_inputs

    def set_logical_function(self, logical_function: str):
        '''
        Sets the logical function of the repressor. In all documentation I've
        only seen NOT and NOR as possible operations, but I've added all
        boolean functions here in case this is just a simplified abstraction.

        Args:
            logical_function: String name correlating to the boolean function.
        '''
        # There's an argument to be made here that's a bit silly and the
        # caller could just directly reference the enumerated logic value,
        # but I don't like the extra cognitive overhead.
        if logical_function == 'AND':
            self.logical_function = LogicFunction.AND
        elif logical_function == 'NOT':
            self.logical_function = LogicFunction.NOT
        elif logical_function == 'OR':
            self.logical_function = LogicFunction.OR
        elif logical_function == 'XOR':
            self.logical_function = LogicFunction.XOR
        elif logical_function == 'NAND':
            self.logical_function = LogicFunction.NAND
        elif logical_function == 'NOR':
            self.logical_function = LogicFunction.NOR
        elif logical_function == 'XNOR':
            self.logical_function = LogicFunction.XNOR
        else:
            raise RuntimeError(
                f'Passed in Logical Function {logical_function} not defined.'
            )

    def get_input_signal_total(self) -> float:
        '''
        Convenience method for getting all input signals into the repressor. We
        add the value of all inputs to get the value of the singal into the
        repressor.

        I don't think you can have more than two inputs but y'know.

        Returns:
            Total input signal to all repressors.

        '''
        return sum(self.get_input_signals())

    def get_input_signals(self) -> List[float]:
        '''
        Gets all input signals into the repressor.

        Returns:
            A list of all input signals into the repressor. All inputs will be
            resolved into floats.
        '''
        computed_input_signals = []
        for input_signal in self.biological_inputs:
            if type(input_signal) == Repressor:
                computed_input_signals.append(input_signal.get_logical_output())
            else:
                computed_input_signals.append(input_signal)
        return computed_input_signals

    def get_logical_output(self):
        '''
        Gets the logical output of the repressor.

        Returns:


        '''
        computed_input_signals = []
        for input_signal in self.logical_inputs:
            if type(input_signal) == Repressor:
                computed_input_signals.append(input_signal.get_logical_output())
            else:
                computed_input_signals.append(input_signal)
        if self.logical_function == LogicFunction.INITIAL:
            raise RuntimeError('Logical Function has not been set.')
        if self.logical_function == LogicFunction.NOT:
            if len(computed_input_signals) > 1:
                raise RuntimeError('Cannot NOT multiple inputs.')
            else:
                return ~computed_input_signals[0] & 0xF
        if len(computed_input_signals) != 2:
            raise RuntimeError(
                'Need two binary inputs to perform logical operations'
            )
        if self.logical_function == LogicFunction.AND:
            return (computed_input_signals[0] & computed_input_signals[1]) & 0xF
        if self.logical_function == LogicFunction.OR:
            return (computed_input_signals[0] | computed_input_signals[1]) & 0xF
        if self.logical_function == LogicFunction.XOR:
            return (computed_input_signals[0] ^ computed_input_signals[1]) & 0xF
        if self.logical_function == LogicFunction.NAND:
            return (~(computed_input_signals[0] & computed_input_signals[1])) & 0xF
        if self.logical_function == LogicFunction.NOR:
            return (~(computed_input_signals[0] | computed_input_signals[1])) & 0xF
        if self.logical_function == LogicFunction.XNOR:
            return (~(computed_input_signals[0] ^ computed_input_signals[1])) & 0xF

    def get_linear_coefficents(self) -> List[float]:
        '''
        Utility function to turn a Repressor into it's coefficents for the
        purpose of visualization.

        Returns:
            A list of all linear coefficents which define the response function
            of a repressor.
        '''
        return [self.y_min, self.y_max, self.k, self.n]

    def get_coefficents(self) -> np.ndarray:
        '''
        Utility function to turn a repressor into it's coefficents for the
        purpose of optimization.

        Returns:
            A numpy array of all of the coefficents for the repressor. These
            are represented in an ndarray of float64 to avoid floating point
            error.

        '''
        return np.asarray(
            [
                self.get_input_signal_total(),
                self.y_min,
                self.y_max,
                self.k,
                self.n,
            ]
        ).astype(np.float64)

    def score_self(self):
        '''
        Function to score efficacy of a gate. Optimization methods call a
        different function, this is purely for understanding the qualities of
        the gate as written.
        '''
        df = pd.DataFrame(columns=['x0', 'x1', 'inputs', 'response'])
        # This makes a lot of assumptions about the problem size we're working
        # with. It might be better to recurse backwards, detect all prior gates
        # and then use the number of gates to determine the size of the logic
        # table.
        logical_inputs = list(itertools.product([0b0, 0b1], repeat=2))
        for logical_input in logical_inputs:
            df_dict = {
                'x0': logical_input[0],
                'x1': logical_input[1],
                'inputs': str(self.get_input_signals()),
                'response': self.calculate_response_function(logical_input)
            }
            df = df.append(df_dict, ignore_index=True)
        print(df)
