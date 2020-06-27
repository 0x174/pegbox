# pegbox/backend/parse_ucf.py
# Parses a user constraint file and generates requisite datastructures.
# TODO: MAKE WORDS GOOD
import json
import pandas as pd
# TODO: Relative imports are bad form.
from ..datastructures import Library


def _pop_and_assign(ucf_entry: dict):
    ucf_entry.pop('collection')
    return ucf_entry


def _pop_and_insert(ucf_entry: dict, container: dict):
    # Some of these don't
    key = None
    if 'name' not in ucf_entry:
        key = len(container) + 1
    else:
        key = ucf_entry['name']
    ucf_entry.pop('collection')
    # Aside from the contents I see no way to discriminate.
    container[key] = ucf_entry


def parse_ucf_file(filepath: str):
    '''


    Args:
        filepath:

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
    # God I don't want to use pandas
    pass



if __name__ == '__main__':
    parse_ucf_file('../../example.json')
