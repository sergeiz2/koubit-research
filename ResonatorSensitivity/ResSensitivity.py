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

class Circuit():
    is_series = None            #True for series circuit, false for parallel.
    L = None                    #Inductance (H)
    C = None                    #Capacitance (F)
    z_in = None                 #Input impedance (Ohm)
    w_r = None                  #Resonant frequency (Hz)
    step_size = None            #Frequency sweep step size (Hz)
    f_sweep = None              #Frequency sweep (Hz)
    w_sweep = None              #Angular frequency sweep (rad/s)
    s11 = None                  #S11 reflection coefficients.
    w_l_bnd = None              #Frequency sweep lower bound (Hz)
    w_u_bnd = None              #Frequency sweep upper bound (Hz)

    def __init__(self, series=None, L=None, C=None, stp_size=1000, z_in=50, w_l_bnd=4e9, w_u_bnd=8e9):
        self.set_LC(L, C)
        self.set_Z_in(z_in)
        self.set_par_or_ser(series)
        self.set_w_l_bnd(w_l_bnd)
        self.set_w_u_bnd(w_u_bnd)
        self.set_stp_size(stp_size)
        self.set_f_sweep(self.get_stp_size())
        self.calc_res_freq()
        self.check_in_bounds(self.get_w_l_bnd(), self.get_w_u_bnd(), self.get_res_freq())

    def __str__(self):
        dict = {'series': 'Yes' if self.get_is_series() else 'No',
                'L': self.get_L(),
                'C': self.get_C(),
                'frequencies': '{} - {} Hz'.format(self.get_w_l_bnd(), self.get_w_u_bnd()),
                'step_size': '{} Hz'.format(self.get_stp_size())
        }

        return str(dict)


    def set_par_or_ser(self, ser=None):
        if ser == None:
            par_or_ser = input("Is this a parallel or a series circuit? (P/S):")

            if par_or_ser == "P" or par_or_ser == "p":
                self.is_series = False

            elif par_or_ser == "S" or par_or_ser == "s":
                self.is_series = True

            else:
                print("Invalid selection!")
                self.set_par_or_ser()

        else:
            is_series = ser

    #TODO: Logic does not account for changing only one of two
    def set_LC(self, ind=None, cap=None):
        if not(ind or cap):
            #NOTE: subdivisions smaller than nH and fF will probably break things.
            if not(ind):
                self.L = float(input("Please input an inductor value (H):"))
            if not(cap):
                self.C = float(input("Please input a capacitor value (in F):"))

        else:
            self.L = ind
            self.C = cap

        print("DEBUG: L={}, C={}".format(self.get_L(), self.get_C()))

    def set_Z_in(self, z_in=None):
        if not(z_in):
            cpx_str = input("Please input an input impedance value (Ohms, in complex form):")
            self.z_in = np.complex128(cpx_str)

        else:
            self.z_in = z_in


    def set_w_l_bnd(self, l_bound=None):
        self.w_l_bnd = l_bound

    def set_w_u_bnd(self, u_bound=None):
        self.w_u_bnd = u_bound

    # TODO: When done debugging, integrate user input into set_w_._bnd()
    # def set_w_l_bnd(self):
    #     self.set_w_l_bnd(float(input("Please enter the lower bound of your frequency sweep (Hz):"))) #Lower bound frequency sweep

    # def set_w_u_bnd(self):
    #     self.set_w_u_bnd(float(input("Please enter the upper bound of your frequency sweep (Hz):"))) #Upper bound frequency sweep

    def get_w_l_bnd(self):
        return self.w_l_bnd

    def get_w_u_bnd(self):
        return self.w_u_bnd

    def get_L(self):
        return self.L

    def get_C(self):
        return self.C

    def get_Z_in(self):
        return self.z_in

    def get_res_freq(self):
        return self.w_r

    def get_is_series(self):
        return self.is_series

    def get_f_sweep(self):
        return self.f_sweep

    def get_w_sweep(self):
        return self.w_sweep

    def get_stp_size(self):
        return self.step_size

    def set_stp_size(self, stp_size=5):
        self.step_size = stp_size

    def calc_res_freq(self):
        self.w_r = 1/(2*np.pi*np.sqrt(self.get_L()*self.get_C()))
        print("The circuit will resonate at a frequency of {} GHz".format(self.get_res_freq()*1e-9))

        print("DEBUG: w_r={}".format(self.get_res_freq()))

    def set_f_sweep(self, step):
        freq_sweep = np.arange(self.get_w_l_bnd(), self.get_w_u_bnd(), step)
        self.f_sweep = freq_sweep
        self.w_sweep = freq_sweep*2*np.pi
        print("DEBUG: f_sweep={}".format(self.get_f_sweep()))

    def check_in_bounds(self, lower_bound=None, upper_bound=None, frequency=None):

        if lower_bound <= frequency <= upper_bound:
            pass
        else:
            print("The resonant frequency of {} GHz is not within your bound of {} GHz to {} GHz. Do you want to change L or C?".format(frequency/1e9, lower_bound/1e9, upper_bound/1e9))
            yes_or_no = input("Y/N:")

            if yes_or_no == "Y" or yes_or_no == "y":
                self.set_LC()
                self.calc_res_freq()
                self.check_in_bounds(self.get_w_l_bnd(), self.get_w_u_bnd(), self.get_res_freq())
            else:
                pass

        print("DEBUG: lower_bound={}={}, upper_bound={}={}, frequency={}={}".format(self.w_l_bnd, lower_bound, self.w_u_bnd, upper_bound, self.get_res_freq(), frequency))

    def calc_z(self):
        series = self.get_is_series()
        ws = self.get_w_sweep()
        zs = np.zeros_like(ws, dtype=np.complex128)
        C = self.get_C()
        L = self.get_L()

        #TODO: Check math
        if series:
            # NEW:
            Z_C = np.complex128(1.0j/(ws*c))
            Z_L = np.complex128(1.0j*ws*L)
            zs = np.sqrt(np.square(Z_L + Z_C))
            # OLD:
            # zs = np.complex128(1.0/ws*C*1j + ws*L*1j)
            # zs[:] = [np.complex128(1.0)/(np.complex128(f*self.get_C()*1j)) + np.complex128(f*self.get_L()*1j) for f in fs]
            # for z, w in zip(zs, self.get_w_sweep()):
                # z = 1.0/(complex(0, w*self.get_C())) + complex(0, w*self.get_L())
            print("DEBUG: series")

        elif not series:
            # NEW:
            zs = np.complex128(-1.0j)*(L/C)/(ws*L - (1.0/(ws*C)) )
            # OLD:
            # zs = np.complex128(1.0/ws*C*1j + 1.0/ws*L*1j)
            # zs[:] = [np.complex128(1.0)/((np.complex128(f*self.get_C())*1j) + 1.0/np.complex128(f*self.get_L()*1j)) for f in fs]
            # for z, w in zip(zs, self.get_w_sweep()):
            #     z = 1.0/((complex(0, w*self.get_C())) + 1.0/complex(0, w*self.get_L()))
            print("DEBUG: not series")

        return zs

    def calc_s11(self):
        gs = np.zeros_like(self.get_w_sweep())
        zs = self.calc_z()
        z_in = self.get_Z_in()

        gs = (z_in - (z_in + zs))/(z_in + (z_in + zs))

        return gs

    def get_slopes(self, gammas=None):
        # Calculates the discrete derivative of S11 w.r.t. frequency and returns the derivative array.
        dgs = np.diff(gammas)/self.get_stp_size()
        dgs = np.abs(dgs)
        dgs = np.append(dgs, dgs[-1])   # Just some dimension housekeeping. Duplicated and appended the last element.

        return dgs

    def find_steep(self, slopes=None, gammas=None):
        # Returns the frequency which corresponds to the steepest part of S11 (to maximize sensitivity.)
        freqs = self.get_w_sweep()
        max_slope = np.max(slopes)
        max_ind = np.argmax(slopes)
        max_freq = freqs[max_ind]

        if max_slope != slopes[max_ind]:
            print("DEBUG: max_slope != slopes[max_ind]")

        return {"frequency": max_freq,
                "derivative": max_slope}

    def plot_s11(self, gammas=None):
        # Plots passed gammas vs the frequencies specified in f_sweep.
        xs = self.get_f_sweep()
        phase = np.angle(gammas)/(2*np.pi)
        mag = np.abs(gammas)

        fig, axs = plt.subplots(2, sharex=True)
        axs[0].plot(xs, mag, 'b')
        axs[0].title.set_text('|S11|')
        axs[0].set(ylabel='Ratio reflected')
        axs[1].plot(xs, phase, 'r')
        axs[1].title.set_text('Arg(S11)')
        axs[1].set(ylabel='rad/2pi')
        plt.xlabel('frequency')

        fig.tight_layout()
        plt.show()
