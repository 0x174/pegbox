"""
backend.datastructures.repressor

Class encapsulating all behavior of a repressor/gate.

W.R. Jackson 2020
"""
import argparse

from backend import parse_ucf_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=''
    )
    parser.add_argument('--input_verilog', type=str, action='store',
        help='Filepath to verilog file.')
    parser.add_argument('--input_ucf', type=str, action='store',
                        help='Filepath to input user constrained file')
    parser.add_argument('--repressor-max', type=int, action='store', default=0,
                        help='Maximum number of repressors that are capable'
                             'of being altered.')
    args = parser.parse_args()
    if args.input_ucf is None:
        raise RuntimeError('Missing UCF File')
    if args.input_verilog is None:
        raise RuntimeError('Missing Verilog File')

    parse_ucf_file(args.input_ucf)





