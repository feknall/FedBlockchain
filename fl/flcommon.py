import numpy as np

feature_vector_length = 784
# Set the input shape
input_shape = (feature_vector_length,)


# ------------------------------------------------------------------------------
# Decimal-Integer Conversion
# ------------------------------------------------------------------------------

def f_to_i(x, scale=1 << 32):
    if x < 0:
        if pow(2, 64) - (abs(x) * (scale)) > (pow(2, 64) - 1):
            return np.uint64(0)
        x = pow(2, 64) - np.uint64(abs(x) * (scale))

    else:
        x = np.uint64(scale * x)

    return np.uint64(x)


def i_to_f(x, scale=1 << 32):
    l = 64
    t = x > (pow(2, (l - 1)) - 1)
    if t:
        x = pow(2, l) - x
        y = np.uint64(x)
        y = np.float32(y * (-1)) / scale

    else:
        y = np.float32(np.uint64(x)) / scale

    return y


f_to_i_v = np.vectorize(f_to_i)
i_to_f_v = np.vectorize(i_to_f)