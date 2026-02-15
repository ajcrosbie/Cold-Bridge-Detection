from ctypes import Array
import numpy as np
import value_calculation
from image import Image
import matplotlib.pyplot as plt

def plot_psis(images: Array[Image]):
    """
    Plots psi-value against external temperature using a 
    set of images as datapoints.
    
    :param images: list of Images ideally taken with different external temperatures
    """

    exts = [i.ext for i in images]
    psis = get_psis(images)

    plt.title("Psi value against external temperature in K")
    plt.xlabel("External temperature, K")
    plt.ylabel("Psi-value")
    # plt.scatter(exts, psis)
    
    poly = np.polyfit(exts, psis, 1)
    line = np.polyval(poly, exts)    

    errs = np.abs(line - psis)
    # plt.plot(exts, np.polyval(poly, exts))
    plt.errorbar(exts, np.polyval(poly, exts), yerr=errs, capsize=5, ecolor="red")

    plt.show()

def get_psis(images: Array[Image]):
    """
    Caclculates psi value for each image in the array.
    
    :param images: array of Images
    :return psis: array of psi values, one corresponding to each image
    """
    # take the surface temperature of each image to be the mean temperature across all pixels
    # labelled as being on the unaffected surface
    surface_temps = np.mean([i.get_sf() for i in images], axis=1)
    exts = [i.ext for i in images]

    psis = np.array([
        value_calculation.calc_psi (i.int_amb, i_ext, i_sfc, i.get_cb(), i.epsilon, i.lx, i.lch) 
        for (i, i_ext, i_sfc) in zip(images, exts, surface_temps)])
    
    return psis

def plot_sensitivies(images: list[Image]):
    """
    Plots sensitivity to external temperature and returns
    
    :param images: Description
    :type images: list[Image]
    """
    # surface temperature of the cold bridge - take to be the mean of all pixel temps
    cb_temps = np.mean([i.get_cb() for i in images], axis=1)
    exts = np.array([i.ext for i in images])

    sens, intercept = np.polyfit(exts, cb_temps, 1)
 
    plt.title("Internal cold bridge surface temperature against external temperature")
    plt.xlabel("External air temp/K")
    plt.ylabel("Surface temp/K")
    plt.scatter(exts, cb_temps)
    plt.plot(exts, exts*sens + intercept)
    plt.show()

    return sens

def rank_cbs_by_psi(cbs: Array[Array[Image]]):
    """
    Ranks a set of cold bridges by their psi value
    
    :param cbs: Array of Image arrays. Each Image array corresponds to one suspected cold bridge
    """

    # Estimate the psi value for each cold bride to be the mean of all calculated psi values
    # TODO: is this a reasonable estimate?    
    psis = np.mean([get_psis for cb in cbs], axis=1)

    # return the cbs and their respective psi value, sorted by psi value
    i = np.argsort(psis)
    return np.zip(cbs[i], psis[i])
