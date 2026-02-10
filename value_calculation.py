import numpy as np
from scipy.constants import g, sigma

def calc_sensitivity(ext_sfc_temp): 
    """
    Calculate the cold bridge's sensitivity to outside temperature changes based on the given external temperatures and surface temperatures.

    Parameters:
    ext_sfc_temp (Dict[float, float]): Dictionary of external to surface temperatures measured at the same time
    Shouldn't matter what units (K or C) but ideally consistent

    Returns:
    sensitivity (float): slope of external temperature compared to surface temperature of cold bridge
    """

    # extract into np arrays
    x, y = zip(*ext_sfc_temp.items())
    x = np.array(x) # external temps
    y = np.array(y) # surface temps

    # check at least 2 data points
    if len(x) < 2:
        raise ValueError("At least two data points required to calculate sensitivity. Please take more photos.")
    
    # linear regression
    slope, _ = np.polyfit(x, y, 1)

    return slope



def calc_frsi(int_sfc_temp, int_amb_temp, ext_temp):
    """
    Calculates the cold bridge's frsi (temperature factor) given external temperature, internal ambient and surface temperatures. 
    Ideally can be mapped over np arrays of these values and then an average taken across all time points.

    Parameters:
    int_sfc_temp (float): internal surface temperature
    int_amb_temp (float): internal ambient temperature
    ext_temp (float): external temperature
    Shouldn't matter what units (K or C) but ideally consistent

    Returns:
    frsi (float): temperature factor (shows condensation and mold risk)
    """

    frsi = (int_sfc_temp - ext_temp) / (int_amb_temp - ext_temp)
    
    return frsi

def calc_psi(int_amb, ext, src, pix_temps, epsilon, lx, lch):
    """
    Calculates the cold bridge's psi-value given internal ambient temperature, external temperature, surrounding radiative temperature (average temperature 
    of surrounding surfaces) and pixel surface temperatures (on cold bridge). 
    Ideally can be mapped over np arrays of these values and then an average taken across all time points.

    Parameters:
    int_amb (float): internal ambient temperature
    ext (float): external temperature
    src (float): surrounding surface temperature
    pix_temps (float[]): temperatures of each pixel in cold bridge
    Should be in K.
    epsilon (float): surface emissivity
    lx (float): pixel length
    lch (float): characteristic length in the vertical direction (total height of wall being analysed)

    Returns:
    psi (float): psi-value
    """

    # defining constants
    # thermal conductivity of air in W / (m.K) - changes with internal ambient temperature at constant pressure which we can assume
    k = 0.0242  + (7.2 * (10 ** -5)) * (int_amb - 273.15) # formula is for celsius
    # kinematic viscosity of air in m^2/s - changes with internal ambiet temperature at constant pressure
    miu = (1.716 * (10 ** -5)) * (273.15 + 110.4) / (int_amb + 110.4) * ((int_amb / 273.15) ** 1.5)
    rho = 101325 / (287 * int_amb)
    nu = miu / rho
    # thermal diffusvity of air in m^2 / s - also at constant pressure
    alpha = k / (rho * 1005) # 1005J/kgK is a typical value for specific heat capacity of dry air at constant pressure for 20-27degC
    # expansion coefficient
    beta = 1 / int_amb
    # use g  and sigma (stephen botzmann) from scipy.constants

    # method set out by O'Grady et al
    tsx = np.array(pix_temps)
    # calculate Rayleigh Number for each pixel 
    rax = g * beta * (int_amb - tsx) * (lch ** 3) / (nu * alpha)

    # calculate Nusselt Number for each pixel 
    nux = (0.825 + (0.387 * (rax ** (1/6))) / (1 + (0.492 * alpha / nu) ** (9/16)) ** (8/27)) ** 2

    # calculate convective coefficient for each pixel
    hcx = nux * k / lch

    # calculate radiative coefficient for each pixel
    hrx = epsilon * sigma * (tsx + src) * (tsx ** 2 + src ** 2)

    # calculate total heat flow rate per pixel - seperating into convection and radiation but using same eqn
    qconv = lx * hcx * (int_amb - tsx)
    qrad = lx * hrx * (src - tsx)
    qx = qconv + qrad

    # identify uniform heat flow
    # SHAKY METHOD!!!!!!!!!
    # assume edges of image (first and last 10 pixels) are the plain non-cold bridge wall
    wall_pixels = np.concatenate((qx[:10], qx[-10:]))
    qxu = np.mean(wall_pixels)

    # calculate thermal bridge heat flow per pixel
    qxtb = qx - qxu

    # calculate total thermal bridge heat flow
    qtb = np.sum(qxtb)

    # calculate psi value
    psi = qtb / (int_amb - ext)

    return psi