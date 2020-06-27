from enum import Enum
import itertools
from typing import (
    List,
    Tuple,
    Union,
)

import numpy as np
import pandas as pd

from backend.datastructures import InputSignal


class LogicTable:

    def __init__(
            self,
            logical_outputs: List[bool],
    ):
        '''
        Only doing two inputs for now.
        Args:
            logical_inputs:
            logical_outputs:
        '''
        self.logical_inputs: List[Tuple[int]] = \
            list(itertools.product([0b0, 0b1], repeat=4))
        self.logical_outputs: List[bool] = logical_outputs


class LogicFunction(Enum):
    NOT = 0
    AND = 1
    OR = 2
    XOR = 3
    NAND = 4
    NOR = 5
    XNOR = 6
    INITIAL = 7


class Repressor:
    # Mathematical attributes that define response function

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
            n: 
            k: 
            y_min: 
            y_max: 
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

        # Our circuitry can have multiple inputs but only a singular output.
        self.chemical_inputs: List[Union[Repressor, Tuple[float, float]]] = []
        self.chemical_output: int = 0

        self.logical_function: LogicFunction = LogicFunction.INITIAL
        self.logical_output: bool = None
        self.logical_inputs: [List[Union[int, Repressor]]] = None

        self.low_on: float = None
        self.high_off: float = None

    # Wonder if you could do RNA interference.

    def calculate_response_function(self, logical_inputs: List[bool]):
        '''

        Returns:

        '''
        current_x = 0
        for index, input_signal in enumerate(self.chemical_inputs):
            if type(input_signal) is Repressor:
                current_x += input_signal.calculate_response_function(
                    [logical_inputs[index]]
                )
            if type(input_signal) is float:
                current_x += input_signal[int(logical_inputs[index])]
        self.chemical_output = self.y_min + (
                (self.y_max - self.y_min) /
                (1.0 + (current_x / self.k) ** self.n)
        )
        return self.chemical_output

    def set_chemical_inputs(
            self,
            chemical_inputs: List[Union[Tuple[float, float], 'Repressor', InputSignal]],
    ):
        '''

        Args:
            chemical_inputs:

        Returns:

        '''
        if len(self.chemical_inputs) + 1 > self.number_of_inputs:
            raise RuntimeError('Too many inputs into gate.')
        input_list = []
        for chemical_input in chemical_inputs:
            if type(chemical_input) == Tuple:
                input_list.append(InputSignal(
                    label='N/A',  # Possibly bad form, I think it would depend on
                    off_value=chemical_input[0],
                    on_value=chemical_input[1],
                ))
            if type(chemical_input) == Repressor or type(chemical_input) == InputSignal:
                input_list.append(chemical_input)
        self.chemical_inputs.extend(chemical_inputs)

    def set_logical_inputs(
            self,
            logical_inputs: List[Union[int, 'Repressor']],
    ):
        '''

        Args:
            logical_inputs:
            low_signal:
            high_signal:

        Returns:

        '''
        self.logical_inputs = logical_inputs

    def set_logical_function(self, logical_function: str):
        '''

        Args:
            logical_function:

        Returns:

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

    def get_input_signal_total(self):
        '''

        Returns:

        '''
        return sum(self.get_input_signals())

    def get_input_signals(self):
        computed_input_signals = []
        for input_signal in self.chemical_inputs:
            if type(input_signal) == Repressor:
                computed_input_signals.append(input_signal.get_logical_output())
            else:
                computed_input_signals.append(input_signal)
        return computed_input_signals

    def get_logical_output(self):
        '''

        Args:
            logic_table:

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

    def get_coefficents(self) -> np:
        '''
        Utility function to turn a Repressor into it's coeficents for the
        purpose of optimization.

        Returns:

        '''
        return np.asarray(
            [
                self.get_input_signal_total(),
                self.y_min,
                self.y_max,
                self.k,
                self.n,
            ]
        )

    def score_self(self):
        '''

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
