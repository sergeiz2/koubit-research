
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import numpy as np
import matplotlib.pyplot as plt
# from numpy import diff

L_l_bnd = 1e-9               #Inductance lower bound
L_u_bnd = 100e-9             #Inductance upper bound
L_step = 1e-9
C_l_bnd = 1e-15              #Capacitance lower bound
C_u_bnd = 100e-15            #Capacitance upper bound
C_step = 1e-15
#FIXME: Duplicated as class variables:
# w_l_bnd = None                  #Frequency sweep lower bound (Hz)
# w_u_bnd = None                  #Frequency sweep upper bound (Hz)

# def find_ideal_C(circ, test_caps=np.arange(C_l_bnd, C_u_bnd, C_step)):
#     Cs = np.arange(C_l_bnd, C_u_bnd, C_step)
#     #TODO: This is confusing series vs is_series?
#     # is_series = circ.get_series()
#     ind = circ.get_L()

#     #TODO: This is confusing series vs is_series?
#     # circ_l_bnd = Circuit(series=is_series, L=ind, C=C_l_bnd)
#     refs_l_bnd = circ_l_bnd.calc_s11()
#     steep_l_bnd = circ_l_bnd.find_steep(refs_l_bnd)

#     circ_r_bnd = Circuit(series=is_series, L=ind, C=C_r_bnd)
#     refs_r_bnd = circ_r_bnd.calc_s11()
#     steep_r_bnd = circ_r_bnd.find_steep(refs_r_bnd)

#     while len(test_caps)>2:
#         if steep_l_bnd.get("derivative") > steep_r_bnd.get("derivative"):
#             new_u_bnd_ind = int(len(test_caps)/2)
#             find_ideal_C(circ, test_caps=test_caps[0:new_u_bnd_ind])
#         elif steep_l_bnd.get("derivative") <  steep_r_bnd.get("derivative"):
#             new_l_bnd_ind = int(len(test_caps)/2)
#             find_ideal_C(circ, test_caps=test_caps[new_l_bnd_ind:-1])
#         else:
#             find_ideal_C(circ, test_caps=test_caps[1:-2])
