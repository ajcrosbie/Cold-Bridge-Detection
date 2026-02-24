from ctypes import Array
import numpy as np
import value_calculation
from image import Image
import matplotlib.pyplot as plt

def plot_psis_single_cb(images: Array[Image]):
    """
    Plots psi-value against external temperature using a 
    set of images as datapoints.
    
    :param images: list of Images ideally taken with different external temperatures
    """
    # Kind of useless as should just be a noisy horizontal line

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
    returns:
    list of (location, psi value array) pairs
    """
    # TODO: ammend to accept location names to display on graph - extend Image with location name?

    psis = np.array([get_psis(cb) for cb in cbs])
    means = np.mean(psis, axis=1)

    # return the cbs and their respective psi value, sorted by psi value
    i = np.argsort(means)   

    plt.show()
    return list(zip(i, psis[i]))

def plot_psis(cbs):
    """   
    Plots a box plot showing psi value for each cold bridge
    
    :param cbs: Array of Image arrays. Each Image array corresponds to one suspected cold bridge
    """

    ranked = rank_cbs_by_psi(cbs)
    locs = [cb[0] for cb in ranked]
    psis = [cb[1] for cb in ranked]

    plt.title("Psi value against location")
    plt.ylabel("Psi, W/mK")
    plt.xlabel("Location")
    plt.boxplot(np.transpose(psis), tick_labels=locs, vert=True)
    plt.show()

def plot_severities(cbs: Array[Array[Image]], high_worse: bool = True):
    """
    Plots box plot of containing the severity of each cold bridge in cbs, on a cale from 0 to 10,
    with 10 being most bad and 0 being ideal

    :param cbs: Array of Image arrays. Each Image array corresponds to one suspected cold bridge
    :param high_worse: boolean. true saying if high severity is bad or good
    
    """

    ranked = rank_cbs_by_psi(cbs)
    locs = [cb[0] for cb in ranked]

    # convert all psi values to severities
    sevs = [psi_to_severity(np.mean(cb[1]), high_worse) for cb in ranked]

    plt.title("Severity rating by location")
    plt.ylim(0, 10)
    plt.ylabel(f"Severity rating (higher {"worse" if high_worse else "better"})")
    plt.xlabel("Location")
    plt.xticks(np.arange(len(sevs)), labels=locs)
    plt.yticks(np.arange(11))

    plt.scatter(np.arange(len(sevs)) ,sevs)
    plt.show()

def plot_frsis(cbs: Array[Array[Image]]):
    """
    Plots box plot of frsi value for each cold bridge in cbs

    :param cbs: array of arrays of images corresponding to the same cold bridge
    """

    # calculates frsi for every image in 2d array cbs
    frsis = np.array([[value_calculation.calc_frsi(np.mean(img.cb_pix), img.int_amb, img.ext) 
                       for img in cb] 
                      for cb in cbs])

    plt.title("Frsi value by location")
    plt.ylabel("Frsi")
    plt.xlabel("Location")
    plt.boxplot(np.transpose(frsis), vert=True)

    plt.show()


def psi_to_severity(psi: float, high_worse = True):
    """
    Returns a severity on a scale from 0 (bad) to 10 (good) given a psi value
    
    :param psi: Psi value (W/mK)
    :return: ranking from 0-10
    """

    # psi values typically range from 0.04 - 0.48 with lower being better.
    psi_low = 0.04
    psi_high = 0.48

    # trim psi to be in this range
    psi = min(psi_high, max(psi, psi_low))

    sev = (psi - psi_low) * 10 / (psi_high-psi_low)

    return sev if high_worse else 10 - sev