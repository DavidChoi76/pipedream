import numpy as np
import scipy.interpolate
from numba import njit
from numba.types import float64, int64, uint32, uint16, uint8, boolean, UniTuple, Tuple, List, DictType, void

geom_code = {
    'circular' : 1,
    'rect_closed' : 2,
    'rect_open' : 3,
    'triangular' : 4,
    'trapezoidal' : 5,
    'parabolic' : 6,
    'elliptical' : 7,
    'wide' : 8,
    'force_main' : 9
}

eps = np.finfo(float).eps

@njit(float64(float64, float64, float64),
      cache=True)
def Circular_A_ik(h_Ik, h_Ip1k, g1):
    """
    Compute cross-sectional area of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Diameter of channel (meters)
    """
    d = g1
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > d:
        y = d
    r = d / 2
    phi = y / r
    if phi < 0:
        phi = 0
    if phi > 2:
        phi = 2
    theta = np.arccos(1 - phi)
    A = r**2 * (theta - np.cos(theta) * np.sin(theta))
    return A

@njit(float64(float64, float64, float64),
      cache=True)
def Circular_Pe_ik(h_Ik, h_Ip1k, g1):
    """
    Compute perimeter of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Diameter of channel (meters)
    """
    d = g1
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > d:
        y = d
    r = d / 2
    phi = y / r
    if phi < 0:
        phi = 0
    if phi > 2:
        phi = 2
    theta = np.arccos(1 - phi)
    Pe = 2 * r * theta
    return Pe

@njit(float64(float64, float64),
      cache=True)
def Circular_R_ik(A_ik, Pe_ik):
    """
    Compute hydraulic radius for link i, superlink k.

    Inputs:
    -------
    A_ik: np.ndarray
        Area of cross section (square meters)
    Pe_ik: np.ndarray
        Wetted perimeter of cross section (meters)
    """
    cond = Pe_ik > 0
    if cond:
        R = A_ik / Pe_ik
    else:
        R = 0
    return R

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Circular_B_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute top width of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Diameter of channel (meters)
    g2: float
        Width of Preissman slot (as a ratio of the diameter)
    """
    d = g1
    pslot = g2
    y = (h_Ik + h_Ip1k) / 2
    # y[y < 0] = 0
    if y < 0:
        y = 0
    r = d / 2
    phi = y / r
    if phi < 0:
        phi = 0
    if phi > 2:
        phi = 2
    theta = np.arccos(1 - phi)
    cond = (y < d)
    if cond:
        B = 2 * r * np.sin(theta)
    else:
        B = pslot * d
    return B


@njit(float64(float64, float64, float64, float64),
      cache=True)
def Rect_Closed_A_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute cross-sectional area of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    """
    y_max = g1
    b = g2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    A = y * b
    return A

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Rect_Closed_Pe_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute perimeter of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    """
    y_max = g1
    b = g2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    Pe = b + 2 * y
    return Pe

@njit(float64(float64, float64),
      cache=True)
def Rect_Closed_R_ik(A_ik, Pe_ik):
    """
    Compute hydraulic radius for link i, superlink k.

    Inputs:
    -------
    A_ik: np.ndarray
        Area of cross section (square meters)
    Pe_ik: np.ndarray
        Wetted perimeter of cross section (meters)
    """
    cond = Pe_ik > 0
    if cond:
        R = A_ik / Pe_ik
    else:
        R = 0
    return R

@njit(float64(float64, float64, float64, float64, float64),
      cache=True)
def Rect_Closed_B_ik(h_Ik, h_Ip1k, g1, g2, g3):
    """
    Compute top width of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    g3: float
        Width of Preissman slot (as a ratio of the width)
    """
    y_max = g1
    b = g2
    pslot = g3
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    cond = (y < y_max)
    if cond:
        B = b
    else:
        B = pslot * b
    return B


@njit(float64(float64, float64, float64, float64),
      cache=True)
def Rect_Open_A_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute cross-sectional area of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    """
    y_max = g1
    b = g2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    A = y * b
    return A

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Rect_Open_Pe_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute perimeter of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    """
    y_max = g1
    b = g2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    Pe = b + 2 * y
    return Pe

@njit(float64(float64, float64),
      cache=True)
def Rect_Open_R_ik(A_ik, Pe_ik):
    """
    Compute hydraulic radius for link i, superlink k.

    Inputs:
    -------
    A_ik: np.ndarray
        Area of cross section (square meters)
    Pe_ik: np.ndarray
        Wetted perimeter of cross section (meters)
    """
    cond = Pe_ik > 0
    if cond:
        R = A_ik / Pe_ik
    else:
        R = 0
    return R

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Rect_Open_B_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute top width of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    """
    y_max = g1
    b = g2
    return b


@njit(float64(float64, float64, float64, float64),
      cache=True)
def Triangular_A_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute cross-sectional area of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Inverse slope of channel sides (run/rise)
    """
    y_max = g1
    m = g2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    A = m * y**2
    return A

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Triangular_Pe_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute perimeter of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Inverse slope of channel sides (run/rise)
    """
    y_max = g1
    m = g2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    Pe = 2 * y * np.sqrt(1 + m**2)
    return Pe

@njit(float64(float64, float64),
      cache=True)
def Triangular_R_ik(A_ik, Pe_ik):
    """
    Compute hydraulic radius for link i, superlink k.

    Inputs:
    -------
    A_ik: np.ndarray
        Area of cross section (square meters)
    Pe_ik: np.ndarray
        Wetted perimeter of cross section (meters)
    """
    cond = Pe_ik > 0
    if cond:
        R = A_ik / Pe_ik
    else:
        R = 0
    return R

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Triangular_B_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute top width of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Inverse slope of channel sides (run/rise)
    """
    y_max = g1
    m = g2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    cond = (y < y_max)
    if cond:
        B = 2 * m * y
    else:
        B = 2 * m * y_max
    return B


@njit(float64(float64, float64, float64, float64, float64),
      cache=True)
def Trapezoidal_A_ik(h_Ik, h_Ip1k, g1, g2, g3):
    """
    Compute cross-sectional area of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    g3: np.ndarray
        Inverse slope of channel sides (run/rise)
    """
    y_max = g1
    b = g2
    m = g3
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    A = y * (b + m * y)
    return A

@njit(float64(float64, float64, float64, float64, float64),
      cache=True)
def Trapezoidal_Pe_ik(h_Ik, h_Ip1k, g1, g2, g3):
    """
    Compute perimeter of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    g3: np.ndarray
        Inverse slope of channel sides (run/rise)
    """
    y_max = g1
    b = g2
    m = g3
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    Pe = b + 2 * y * np.sqrt(1 + m**2)
    return Pe

@njit(float64(float64, float64),
      cache=True)
def Trapezoidal_R_ik(A_ik, Pe_ik):
    """
    Compute hydraulic radius for link i, superlink k.

    Inputs:
    -------
    A_ik: np.ndarray
        Area of cross section (square meters)
    Pe_ik: np.ndarray
        Wetted perimeter of cross section (meters)
    """
    cond = Pe_ik > 0
    if cond:
        R = A_ik / Pe_ik
    else:
        R = 0
    return R

@njit(float64(float64, float64, float64, float64, float64),
      cache=True)
def Trapezoidal_B_ik(h_Ik, h_Ip1k, g1, g2, g3):
    """
    Compute top width of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    g3: np.ndarray
        Inverse slope of channel sides (run/rise)
    """
    y_max = g1
    b = g2
    m = g3
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    cond = (y < y_max)
    if cond:
        B = b + 2 * m * y
    else:
        B = b + 2 * m * y_max
    return B

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Parabolic_A_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute cross-sectional area of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    """
    y_max = g1
    b = g2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    A = 2 * b * y / 3
    return A

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Parabolic_Pe_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute perimeter of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    """
    y_max = g1
    b = g2
    y = (h_Ik + h_Ip1k) / 2
    if y <= 0:
        y = eps
    if y > y_max:
        y = y_max
    x = 4 * y / b
    Pe = (b / 2) * (np.sqrt(1 + x**2) + (1 / x) * np.log(x + np.sqrt(1 + x**2)))
    return Pe

@njit(float64(float64, float64),
      cache=True)
def Parabolic_R_ik(A_ik, Pe_ik):
    """
    Compute hydraulic radius for link i, superlink k.

    Inputs:
    -------
    A_ik: np.ndarray
        Area of cross section (square meters)
    Pe_ik: np.ndarray
        Wetted perimeter of cross section (meters)
    """
    cond = Pe_ik > 0
    if cond:
        R = A_ik / Pe_ik
    else:
        R = 0
    return R

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Parabolic_B_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute top width of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    """
    y_max = g1
    b = g2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    B = b * np.sqrt(y / y_max)
    return B

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Elliptical_A_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute cross-sectional area of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Full height of channel (meters)
    g2: np.ndarray
        Full width of channel (meters)
    """
    y_max = g1
    b = g1 / 2
    a = g2 / 2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    theta = np.arcsin((y - b) / b)
    A_a = a * b * (np.pi / 2 + theta)
    A_b = a * b * np.cos(theta) * np.sin(theta)
    A = A_a + A_b
    return A

@njit(float64(float64, float64),
      cache=True)
def Elliptical_R_ik(A_ik, Pe_ik):
    """
    Compute hydraulic radius for link i, superlink k.

    Inputs:
    -------
    A_ik: np.ndarray
        Area of cross section (square meters)
    Pe_ik: np.ndarray
        Wetted perimeter of cross section (meters)
    """
    cond = Pe_ik > 0
    if cond:
        R = A_ik / Pe_ik
    else:
        R = 0
    return R

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Elliptical_B_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute top width of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Full height of channel (meters)
    g2: np.ndarray
        Full width of channel (meters)
    """
    y_max = g1
    b = g1 / 2
    a = g2 / 2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    theta = np.arcsin((y - b) / b)
    B = 2 * np.cos(theta) * np.sqrt(a**2 * np.cos(theta)**2
                                    + b**2 * np.sin(theta)**2)
    return B


@njit(float64(float64, float64, float64, float64),
      cache=True)
def Wide_A_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute cross-sectional area of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    """
    y_max = g1
    b = g2
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    A = y * b
    return A

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Wide_Pe_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute perimeter of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    """
    b = g2
    Pe = b
    return Pe

@njit(float64(float64, float64),
      cache=True)
def Wide_R_ik(A_ik, Pe_ik):
    """
    Compute hydraulic radius for link i, superlink k.

    Inputs:
    -------
    A_ik: np.ndarray
        Area of cross section (square meters)
    Pe_ik: np.ndarray
        Wetted perimeter of cross section (meters)
    """
    cond = Pe_ik > 0
    if cond:
        R = A_ik / Pe_ik
    else:
        R = 0
    return R

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Wide_B_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute top width of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Width of channel (meters)
    """
    y_max = g1
    b = g2
    return b

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Force_Main_A_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute cross-sectional area of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Diameter of channel (meters)
    g2: np.ndarray
        Width of Preissman slot (as a ratio of the diameter)
    """
    d = g1
    r = d / 2
    A = np.pi * r**2
    return A

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Force_Main_Pe_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute perimeter of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Diameter of channel (meters)
    g2: np.ndarray
        Width of Preissman slot (as a ratio of the diameter)
    """
    d = g1
    Pe = np.pi * d
    return Pe

@njit(float64(float64, float64),
      cache=True)
def Force_Main_R_ik(A_ik, Pe_ik):
    """
    Compute hydraulic radius for link i, superlink k.

    Inputs:
    -------
    A_ik: np.ndarray
        Area of cross section (square meters)
    Pe_ik: np.ndarray
        Wetted perimeter of cross section (meters)
    """
    cond = Pe_ik > 0
    if cond:
        R = A_ik / Pe_ik
    else:
        R = 0
    return R

@njit(float64(float64, float64, float64, float64),
      cache=True)
def Force_Main_B_ik(h_Ik, h_Ip1k, g1, g2):
    """
    Compute top width of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Diameter of channel (meters)
    g2: np.ndarray
        Width of Preissman slot (as a ratio of the diameter)
    """
    d = g1
    pslot = g2
    B = pslot * d
    return B

@njit(float64(float64, float64, float64, float64, float64, float64, float64, float64),
      cache=True)
def Floodplain_A_ik(h_Ik, h_Ip1k, g1, g2, g3, g4, g5, g6):
    """
    Compute cross-sectional area of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Height of floodplain section above channel bottom (meters)
    g3: np.ndarray
        Width of lower channel bottom (meters)
    g4: np.ndarray
        Width of upper channel bottom (meters)
    g5: np.ndarray
        Inverse slope of lower channel sides (run/rise)
    g6: np.ndarray
        Inverse slope of upper channel sides (run/rise)
    """
    y_max = g1
    y_mid = g2
    b_lower = g3
    b_upper = g4
    m_lower = g5
    m_upper = g6
    y = (h_Ik + h_Ip1k) / 2
    if y < 0.:
        y = 0.
    if y > y_max:
        y = y_max
    if y < y_mid:
        y_lower = y
        y_upper = 0.
    elif y >= y_mid:
        y_lower = y_mid
        y_upper = y - y_mid
    A_lower = y_lower * (b_lower + m_lower * y_lower)
    A_upper = y_upper * (b_upper + m_upper * y_upper)
    A = A_lower + A_upper
    return A

@njit(float64(float64, float64, float64, float64, float64, float64, float64, float64),
      cache=True)
def Floodplain_Pe_ik(h_Ik, h_Ip1k, g1, g2, g3, g4, g5, g6):
    """
    Compute perimeter of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Height of floodplain section above channel bottom (meters)
    g3: np.ndarray
        Width of lower channel bottom (meters)
    g4: np.ndarray
        Width of upper channel bottom (meters)
    g5: np.ndarray
        Inverse slope of lower channel sides (run/rise)
    g6: np.ndarray
        Inverse slope of upper channel sides (run/rise)
    """
    y_max = g1
    y_mid = g2
    b_lower = g3
    b_upper = g4
    m_lower = g5
    m_upper = g6
    y = (h_Ik + h_Ip1k) / 2
    b_mid = b_lower + 2 * m_lower * y_mid
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    if y < y_mid:
        y_lower = y
        y_upper = 0.
        k = 0.
    elif y >= y_mid:
        y_lower = y_mid
        y_upper = y - y_mid
        k = 1.
    Pe_lower = b_lower + 2 * y_lower * np.sqrt(1 + m_lower**2)
    Pe_upper = k * (b_upper - b_mid) + 2 * y_upper * np.sqrt(1 + m_upper**2)
    Pe = Pe_lower + Pe_upper
    return Pe

@njit(float64(float64, float64),
      cache=True)
def Floodplain_R_ik(A_ik, Pe_ik):
    """
    Compute hydraulic radius for link i, superlink k.

    Inputs:
    -------
    A_ik: np.ndarray
        Area of cross section (square meters)
    Pe_ik: np.ndarray
        Wetted perimeter of cross section (meters)
    """
    cond = Pe_ik > 0
    if cond:
        R = A_ik / Pe_ik
    else:
        R = 0
    return R

@njit(float64(float64, float64, float64, float64, float64, float64, float64, float64),
      cache=True)
def Floodplain_B_ik(h_Ik, h_Ip1k, g1, g2, g3, g4, g5, g6):
    """
    Compute top width of flow for link i, superlink k.

    Inputs:
    -------
    h_Ik: np.ndarray
        Depth at upstream junction (meters)
    h_Ip1k: np.ndarray
        Depth at downstream junction (meters)
    g1: np.ndarray
        Height of channel (meters)
    g2: np.ndarray
        Height of floodplain section above channel bottom (meters)
    g3: np.ndarray
        Width of lower channel bottom (meters)
    g4: np.ndarray
        Width of upper channel bottom (meters)
    g5: np.ndarray
        Inverse slope of lower channel sides (run/rise)
    g6: np.ndarray
        Inverse slope of upper channel sides (run/rise)
    """
    y_max = g1
    y_mid = g2
    b_lower = g3
    b_upper = g4
    m_lower = g5
    m_upper = g6
    y = (h_Ik + h_Ip1k) / 2
    if y < 0:
        y = 0
    if y > y_max:
        y = y_max
    if y < y_mid:
        y_lower = y
        B = b_lower + 2 * m_lower * y_lower
    elif y >= y_mid:
        y_upper = y - y_mid
        B = b_upper + 2 * m_upper * y_upper
    return B


