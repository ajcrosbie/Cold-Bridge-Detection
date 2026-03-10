import numpy as np
from . import value_calculation
from .image import Image
import matplotlib.pyplot as plt
from scipy import stats
import os

# path to the folder in which any plots will be saved
GRAPHPATH = "plots/"


# syncs plot files to disk so that the frontend always fetches the right plots
def sync_file(path: str):
    with open(path, "r+b") as f:
        os.fsync(f.fileno())

def plot_psis_single_cb(images: list[Image], show=False) -> str:
    """
    Plots psi-value against external temperature using a 
    set of images as datapoints.
    
    :param images: list of Images ideally taken with different external temperatures
    """

    path = f'{GRAPHPATH}singleImgPsi.png'
#    Kind of useless as should just be a noisy horizontal line

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

    if show:
        plt.show()
    else:
        plt.savefig(path)
        sync_file(path)
        plt.close()

    return path

def get_psis(images: list[Image]) -> np.ndarray:
    """
    Caclculates psi value for each image in the array.
    
    :param images: array of Images
    :return psis: array of psi values, one corresponding to each image
    """
    # take the surface temperature of each image to be the mean temperature across all pixels
    # labelled as being on the unaffected surface
    surface_temps = [i.sf_temp for i in images]
    exts = [i.ext for i in images]

    print(f"surface_temps={surface_temps}, exts={exts}")
    for i in images:
        print(f"mean={np.mean(i.get_cb())}")

    # calculate psi value for every image and return as a np array
    psis = np.array([
        value_calculation.calc_psi (i.int_amb, i_ext, i_sfc, i.get_cb(), i.epsilon, i.lx, i.lch) 
        for (i, i_ext, i_sfc) in zip(images, exts, surface_temps)])
    
    return psis

def plot_sensitivities(images: list[Image], location: str = "", show: bool =False) -> str:
    """
    Plots sensitivity to external temperature and returns path to the image
    
    :param images: Description
    :type images: list[Image]
    """

    if len(images) == 1:
        return ""

    path = f"{GRAPHPATH}sensitivity{'_'+location if location else ''}" + ".png"

    # surface temperature of the cold bridge - take to be the mean of all pixel temps
    # cb_temps = np.mean([i.get_cb() for i in images], axis=1)
    cb_temps = [np.mean(i.get_cb()) for i in images]
    exts = np.array([i.ext for i in images])

    # calculate best fit line
    # TODO: probably shouldn't be order 1
    sens, intercept = np.polyfit(exts, cb_temps, 1)
 
    plt.title("Internal cold bridge surface temperature against external temperature")
    plt.xlabel("External air temp/°C")
    plt.ylabel("Surface temp/°C")
    with open("Backendlogs.txt", "a") as f:

        f.writelines(str(exts))
        f.writelines(str(cb_temps))

    print(exts)
    print(cb_temps)
    plt.scatter(exts, cb_temps)

    # plots best fit line
    plt.plot(exts, exts*sens + intercept)
    if show:
        plt.show()
    else:
        plt.savefig(path)
        sync_file(path)
        plt.close()

    return path

def rank_cbs_by_psi(cbs: dict[str, list[Image]]) -> list[tuple[str, float, float, np.ndarray]]:
    """
    Ranks a set of cold bridges by their psi value
    
    :param cbs: Dictionary mapping location names to lists of Images. Each Image list corresponds to one suspected cold bridge
    returns:
    list of (location, mean_psi, moe, psi_array) tuples sorted most to least severe
    """
    
    results = []

    for location, cb_images in cbs.items():
        psis = get_psis(cb_images)
        mean_psi, moe = calculate_psi_ci(psis)

        results.append((location, mean_psi, moe, psis)) # box plots can use all the data points

    results.sort(key=lambda x: x[1], reverse=True) # descending order

    return results

def plot_psis(cbs: dict[str, list[Image]], show: bool=False) -> str:
    """   
    Plots a box plot showing psi value for each cold bridge
    
    :param cbs: Array of Image arrays. Each Image array corresponds to one suspected cold bridge
    """
    path = f'{GRAPHPATH}psis.png'
    ranked = rank_cbs_by_psi(cbs)
    locs = [cb[0] for cb in ranked]
    psis = [cb[3] for cb in ranked]

    plt.title("Psi value against location")
    plt.ylabel("Psi, W/mK")
    plt.xlabel("Location")
    plt.boxplot(np.transpose(psis), tick_labels=locs, vert=True)

    # either draw graph to display or save to file
    if show:
        plt.show()
    else:
        plt.savefig(path)
        sync_file(path)
        plt.close()

    return path

def plot_severities(cbs: dict[str, list[Image]], high_worse: bool = True, show: bool =False, bar: bool = True) -> str:
    """
    Plots box plot of containing the severity of each cold bridge in cbs, on a cale from 0 to 10,
    By default, 10 is most severe and 0 being ideal

    :param cbs: Each Image array corresponds to one suspected cold bridge
    :param high_worse: (boolean) saying if high severity is bad or good
    
    """
    path = f'{GRAPHPATH}severities.png'
    ranked = rank_cbs_by_psi(cbs)
    locs = [cb[0] for cb in ranked]

    # convert all psi values to severities
    sevs = [psi_to_severity(cb[1], high_worse) for cb in ranked]

    plt.title("Severity rating by location")
    plt.ylim(0, 10)
    plt.ylabel(f"Severity rating (higher {"worse" if high_worse else "better"})")
    plt.xlabel("Location")

    if bar:
        plt.bar(locs, sevs)
    else:
        # categorical data so only need a tick at each location
        plt.xticks(np.arange(len(sevs)), labels=locs)
        # y tick for each of 0-10 inclusive
        plt.yticks(np.arange(11))

        plt.scatter(np.arange(len(sevs)), sevs)

    if show:
        plt.show()
    else:
        
        plt.savefig(path)
        sync_file(path)
        plt.close()

    return path

def plot_frsis(cbs: dict[str, list[Image]], show: bool =False) -> str:
    """
    Plots box plot of frsi value for each cold bridge in cbs

    :param cbs: array of arrays of images corresponding to the same cold bridge
    """
    path = f'{GRAPHPATH}frsis.png'
    locs = list(cbs.keys())

    # calculates frsi for every image in 2d array cbs
    frsis = np.array([[value_calculation.calc_frsi(float(np.mean(img.cb_pix)), img.int_amb, img.ext) 
                       for img in cb_images] 
                      for cb_images in cbs.values()])

    plt.title("Frsi value by location")
    plt.ylabel("Frsi")
    plt.xlabel("Location")

    plt.boxplot(np.transpose(frsis), tick_labels=locs, vert=True)

    if show:
        plt.show()
    else:
        plt.savefig(path)
        sync_file(path)
        plt.close()
        
    return path

def psi_to_severity(psi: float, high_worse: bool = True) -> float:
    """
    Returns a severity on a scale from 0 to 10 given a psi value
    By default high values are more severe
    
    :param psi: Psi value (W/mK)
    :return: ranking from 0-10
    """

    # psi values typically range from 0.04 - 0.48 with lower being better.
    psi_low = 0.0
    psi_high = 0.5

    # trim psi to be in this range
    psi = min(psi_high, max(psi, psi_low))

    sev = 0.5 + (psi - psi_low) * 9.5 / (psi_high-psi_low)

    # flip severity if high_worse=False
    return sev if high_worse else 10 - sev

def calculate_psi_ci(psis: np.ndarray, confidence_level: float = 0.95) -> tuple[float, float]:
    """
    Calculates the mean psi-value and its confidence interval margin of error.
    
    :param psis: Array of calculated psi-values for a single cold bridge
    :param confidence_level: The desired confidence level (default 95%)
    :return: A tuple containing (mean_psi, moe)
    """
    n = len(psis)

    if n < 2:
        return (float(np.mean(psis)), 0.0)
    
    mean_psi = np.mean(psis)
    std_dev = np.std(psis, ddof=1)

    # calculate standard error of mean
    sem = std_dev/ np.sqrt(n)

    # degrees of freedom
    df = n-1

    # t-test (small sample size) so
    # t-score for confidence interval (two-tailed)
    alpha = 1 - confidence_level
    t_score = stats.t.ppf(1 - alpha/2, df)

    # margin of error
    moe = t_score * sem

    return float(mean_psi), float(moe)
