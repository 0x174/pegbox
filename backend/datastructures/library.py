import dataclasses


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                super(Singleton,
                      cls).__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclasses.dataclass
class Library(metaclass=Singleton):
    '''
    This Singleton represents the entirety of our active library.
    '''
    # If this were angled more toward a sustained/production code base I would
    # probably have defined dataclasses/schemas for all of the underlying
    # fields.
    header: dict = None
    measurement_std: dict = None
    logic_constraints: dict = None
    device_rules: dict = None
    circuit_rules: dict = None
    genetic_locations: dict = None

    motifs: dict = None
    gates: dict = None
    models: dict = None
    structures: dict = None
    parts: dict = None
    functions: dict = None


