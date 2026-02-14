import numpy as np
import value_calculation
from image import Image
import matplotlib.pyplot as plt

def plot_psis(images: list[Image]):
    """
    Plots psi-value against external temperature using a 
    set of images as datapoints.
    
    :param images: list of Images ideally taken with different external temperatures
    """

    surface_temps = np.mean([i.get_sf() for i in images], axis=1)
    exts = [i.ext for i in images]

    psis = [value_calculation.calc_psi (i.int_amb, i_ext, i_sfc, i.get_cb(), i.epsilon, i.lx, i.lch) 
            for (i, i_ext, i_sfc) in zip(images, exts, surface_temps)]

    plt.scatter(exts, psis)

    return psis
