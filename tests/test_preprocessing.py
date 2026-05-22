
import numpy as np

def test_shape():
    img = np.zeros((100,100))
    assert img.shape == (100,100)
