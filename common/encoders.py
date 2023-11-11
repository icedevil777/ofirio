import numpy as np
from django.core.serializers.json import DjangoJSONEncoder


class DjangoNumpyJSONEncoder(DjangoJSONEncoder):
    """Encodes also numpy types, in addition to standart and Django behavior"""
    np_ints = (
        np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16,
        np.uint32, np.uint64,
    )
    np_floats = np.float_, np.float16, np.float32, np.float64
    np_complexes = np.complex_, np.complex64, np.complex128

    def default(self, obj):
        if isinstance(obj, self.np_ints):
            return int(obj)

        elif isinstance(obj, self.np_floats):
            return float(obj)

        elif isinstance(obj, self.np_complexes):
            return {'real': obj.real, 'imag': obj.imag}

        elif isinstance(obj, np.ndarray):
            return obj.tolist()

        elif isinstance(obj, np.bool_):
            return bool(obj)

        elif isinstance(obj, np.void):
            return None

        return super().default(obj)
