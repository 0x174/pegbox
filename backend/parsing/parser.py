"""
backend.parsing.parser

Functionality responsible for parsing UCF and Verilog files for the purpose
of intake into the optimization program as a whole.

W.R. Jackson 2020
"""
import json
from backend.datastructures import (
    Library,
)


def _pop_and_assign(ucf_entry: dict) -> dict:
    '''
    Convenience function to remove some of the spurious data from the JSON and
    then return the value. Done to reduce boilerplate in parsing function.

    Args:
        ucf_entry: The input dictionary to remove values from.

    Returns:
        The input dictionary sans collection field.
    '''
    ucf_entry.pop('collection')
    return ucf_entry


def _pop_and_insert(ucf_entry: dict, container: dict):
    '''
    Removes spurious data from input dictionary, generates a label if one
    does not exist, and then assigns the value to the passed in container
    dictionary.

    Args:
        ucf_entry: The input dictionary from the UCF file.
        container: The container endpoint for the dictionary.

    '''
    if 'name' not in ucf_entry:
        key = len(container) + 1
    else:
        key = ucf_entry['name']
    ucf_entry.pop('collection')
    # Aside from the contents I see no way to discriminate.
    container[key] = ucf_entry


def parse_ucf_file(filepath: str):
    '''
    Parses in the passed in UCF (User Constraint File). Files are assigned
    to a global singleton due to the UCF acting as the global point of reference
    for the optimization program.

    Args:
        filepath: The filepath to the UCF FIle.

    Returns:

    '''
    # The underlying JSON is unordered so we need to parse it to create our
    # datastructures. This is represented by a classification in the collection
    # key of the JSON file. Some of these elements appear only once while others
    # are collections.
    lib = Library()

    # Multiple Elements
    motif_library = {}
    gates = {}
    models = {}
    structures = {}
    parts = {}
    functions = {}
    with open(filepath, 'r') as input_file:
        contents = json.loads(input_file.read())
        for entry in contents:
            # Could just be the file I got, but there is some numeric elements
            # at the top level that I'm unsure the purpose of.
            if 'collection' in entry:
                classification = entry['collection']
                if classification == 'header':
                    lib.header = _pop_and_assign(entry)
                if classification == 'measurement_std':
                    lib.measurement_std = _pop_and_assign(entry)
                if classification == 'logic_constraints':
                    lib.logic_constraints = _pop_and_assign(entry)
                if classification == 'device_rules':
                    lib.device_rules = _pop_and_assign(entry)
                if classification == 'circuit_rules':
                    lib.circuit_rules = _pop_and_assign(entry)
                if classification == 'genetic_locations':
                    lib.genetic_locations = _pop_and_assign(entry)
                # Begin Multiple
                if classification == 'motif_library':
                    _pop_and_insert(entry, motif_library)
                if classification == 'gates':
                    _pop_and_insert(entry, gates)
                if classification == 'models':
                    _pop_and_insert(entry, models)
                if classification == 'structures':
                    _pop_and_insert(entry, structures)
                if classification == 'parts':
                    _pop_and_insert(entry, parts)
                if classification == 'functions':
                    _pop_and_insert(entry, functions)
    # Some of the above are not useful in our optimization problem but could
    # be useful if this were further expanded in the future.
    for library in motif_library:
        pass
    for gate in gates:
        pass
    for model in models:
        pass
    for structure in structures:
        pass
    for part in parts:
        pass
    for function in functions:
        pass

def parse_verilog_file():
    '''

    Returns:

    '''
    pass
