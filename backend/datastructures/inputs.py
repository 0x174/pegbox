from dataclasses import dataclass


@dataclass
class InputSignal:
    label: str
    on_value: float
    off_value: float
    binary_value: int = None

    def __len__(self):
        return 1

    def set_binary_value(self, binary_value: int):
        '''

        Returns:

        '''
        self.binary_value = binary_value

if __name__ == '__main__':
    p1 = InputSignal(
        label='pTet',
        on_value=0.0013,
        off_value=4.4,
    )


