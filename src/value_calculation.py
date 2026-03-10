import numpy as np
from scipy.constants import g, sigma

#FIXME: do we want to add errors for incorrect values?

def calc_sensitivity(ext_sfc_temp: dict[float, float]) -> float: 
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

def calc_frsi(int_sfc_temp: float, int_amb_temp: float, ext_temp: float) -> float:
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

def calc_psi(int_amb: float, ext: float, t_wall: float, pix_temps: np.ndarray, epsilon: float, lx: float, lch: float) -> float:
    """
    Calculates the cold bridge's psi-value given internal ambient temperature, external temperature, surrounding radiative temperature (average temperature 
    of surrounding surfaces) and pixel surface temperatures (on cold bridge). 
    Ideally can be mapped over np arrays of these values and then an average taken across all time points.

    Parameters:
    int_amb (float): internal ambient temperature (in celcius)
    ext (float): external temperature (in celcius)
    t_wall (float): surrounding surface temperature of non-cb wall (in celcius)
    pix_temps (np.ndarray): temperatures of each pixel in cold bridge (in celcius)
    Should be in K, but all are received in Celcius, so convert at
    epsilon (float): surface emissivity
    lx (float): pixel length
    lch (float): characteristic length in the vertical direction (total height of wall being analysed)

    Returns:
    psi (float): psi-value
    """
    print(f"pix_temps={pix_temps}")
    # TODO: MAKE NEATER
    # converting all celcius temps we receive to kelvin
    int_amb = int_amb + 273.15
    ext = ext + 273.15
    t_wall = t_wall + 273.15
    pix_temps = pix_temps + 273.15


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
    #total heat flow for cold bridge (qx)
    # calculate Rayleigh Number for each pixel 
    rax = g * beta * (int_amb - pix_temps) * (lch ** 3) / (nu * alpha)

    # calculate Nusselt Number for each pixel 
    nux = (0.825 + (0.387 * (np.abs(rax) ** (1/6))) / (1 + (0.492 * alpha / nu) ** (9/16)) ** (8/27)) ** 2

    # calculate convective coefficient for each pixel
    hcx = nux * k / lch

    # calculate radiative coefficient for each pixel
    # using int_amb as the surrounfing radiative temperature
    hrx = epsilon * sigma * (pix_temps + int_amb) * (pix_temps ** 2 + int_amb ** 2)

    # calculate total heat flow rate per pixel - seperating into convection and radiation but using same eqn
    qconv = lx * hcx * (int_amb - pix_temps)
    qrad = lx * hrx * (int_amb - pix_temps)
    qx = qconv + qrad

    # identify uniform heat flow
    # calculate Rayleigh and Nusselt Numbers for the non-cb wall using src
    rax_u = g * beta * (int_amb - t_wall) * (lch ** 3) / (nu * alpha)
    nux_u = (0.825 + (0.387 * (np.abs(rax_u) ** (1/6))) / (1 + (0.492 * alpha / nu) ** (9/16)) ** (8/27)) ** 2
    
    # calculate convective coefficient for non-cb wall
    hcx_u = nux_u * k / lch
    
    # calculate radiative coefficient for non-cb wall
    # unaffected wall receives radiation from room (int_amb)
    hrx_u = epsilon * sigma * (t_wall + int_amb) * (t_wall ** 2 + int_amb ** 2)
    
    # calculate uniform baseline heat flow per pixel (qxu)
    qconv_u = lx * hcx_u * (int_amb - t_wall)
    qrad_u = lx * hrx_u * (int_amb - t_wall) # this evaluates to 0, as expected for no temp difference
    qxu = qconv_u + qrad_u 

    # calculate thermal bridge heat flow per pixel
    qxtb = qx - qxu

    # calculate total thermal bridge heat flow
    # heat loss along a line
    qtb = np.mean(np.sum(qxtb, axis=0))

    if int_amb == ext:
        return 0.0  # how do we want to handle this its an invalid input tbh
    # calculate psi value
    psi = qtb / (int_amb - ext)

    return float(psi)

def calc_pixel_length(camera: str, distance: float = 2.0) -> float:
    camera_profiles = {
        "FLIR E40bx": {"fov": 25.0, "res": 320},
        "HIKMICRO M11W": {"fov": 37.2, "res": 640}
    }

    if camera not in camera_profiles:
        raise ValueError(f"Unsupported camera type: '{camera}'. Please select from: {list(camera_profiles.keys())}")


    horizontal_fov = camera_profiles[camera]["fov"]
    horizontal_res = camera_profiles[camera]["res"]
    
    # slight change from toby's maths (that assumes wall curves around camera, not a plane)
    pixel_size = (2 * distance * np.tan(np.deg2rad(horizontal_fov / 2))) / horizontal_res

    return pixel_size
