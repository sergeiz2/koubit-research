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

def find_ideal_C(circ, test_caps=np.arange(C_l_bnd, C_u_bnd, C_step)):
    Cs = np.arange(C_l_bnd, C_u_bnd, C_step)
    is_series = circ.get_series()
    ind = circ.get_L()

    circ_l_bnd = Circuit(series=is_series, L=ind, C=C_l_bnd)
    refs_l_bnd = circ_l_bnd.calc_s11()
    steep_l_bnd = circ_l_bnd.find_steep(refs_l_bnd)

    circ_r_bnd = Circuit(series=is_series, L=ind, C=C_r_bnd)
    refs_r_bnd = circ_r_bnd.calc_s11()
    steep_r_bnd = circ_r_bnd.find_steep(refs_r_bnd)

    while len(test_caps)>2:
        if steep_l_bnd.get("derivative") > steep_r_bnd.get("derivative"):
            new_u_bnd_ind = int(len(test_caps)/2)
            find_ideal_C(circ, test_caps=test_caps[0:new_u_bnd_ind])
        elif steep_l_bnd.get("derivative") <  steep_r_bnd.get("derivative"):
            new_l_bnd_ind = int(len(test_caps)/2)
            find_ideal_C(circ, test_caps=test_caps[new_l_bnd_ind:-1])
        else:
            find_ideal_C(circ, test_caps=test_caps[1:-2])

class Circuit():
    series = None               #True for series circuit, false for parallel.
    L = None                    #Inductance (H)
    C = None                    #Capacitance (F)
    z_in = None                 #Input impedance (Ohm)
    w_r = None                  #Resonant frequency (Hz)
    step_size = None            #Frequency sweep step size (Hz)
    f_sweep = None              #Frequency sweep (Hz)
    s11 = None                  #S11 reflection coefficients.
    w_l_bnd = None              #Frequency sweep lower bound (Hz)
    w_u_bnd = None              #Frequency sweep upper bound (Hz)

    def __init__(self, series=None, L=None, C=None, stp_size=5, w_l_bnd=4e9, w_u_bnd=8e9):
        self.set_LC(L, C)
        self.set_par_or_ser(series)
        self.set_w_l_bnd(w_l_bnd)
        self.set_w_u_bnd(w_u_bnd)
        self.set_f_sweep(stp_size)
        self.set_res_freq(self.get_L(), self.get_C())
        self.check_in_bounds(self.get_w_l_bnd(), self.get_w_u_bnd(), self.get_res_freq())

    def set_par_or_ser(self, ser=None):
        if ser == None:
            par_or_ser = input("Is this a parallel or a series circuit? (P/S):")

            if par_or_ser == "P" or par_or_ser == "p":
                self.series = False

            elif par_or_ser == "S" or par_or_ser == "s":
                self.series = True

            else:
                print("Invalid selection!")
                self.set_par_or_ser()

        else:
            series = ser

    #TODO: Logic does not account for changing only one of two
    def set_LC(self, ind=None, cap=None):
        if not(ind or cap):
            self.L = float(input("Please input an inductor value (H):"))
            self.C = float(input("Please input a capacitor value (in F):"))
            #NOTE: subdivisions smaller than nH and fF will probably break things.

        else:
            self.L = ind
            self.C = cap

        print("DEBUG: L={}, C={}".format(self.get_L(), self.get_C()))

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

    def get_res_freq(self):
        return self.w_r

    def get_series(self):
        return self.series

    def get_f_sweep(self):
        return self.f_sweep

    def set_res_freq(self, inductance, capacitance):
        self.w_r = 1/(np.sqrt(self.get_L()*self.get_C()))
        print("The circuit will resonate at a frequency of {} GHz".format(self.get_res_freq()/10e9))

        print("DEBUG: w_r={}".format(self.get_res_freq()))

    def set_f_sweep(self, step):
        self.f_sweep = np.arange(self.get_w_l_bnd(), self.get_w_u_bnd(), step)
        print("DEBUG: f_sweep={}".format(self.get_f_sweep()))

    def check_in_bounds(self, lower_bound, upper_bound, frequency):

        if lower_bound <= frequency <= upper_bound:
            pass
        else:
            print("The resonant frequency is not within your bounds. Do you want to change L or C?")
            yes_or_no = input("Y/N:")

            if yes_or_no == "Y" or yes_or_no == "y":
                self.set_LC()
                self.set_res_freq(self.get_L(), self.get_C())
                self.check_in_bounds(self.get_w_l_bnd(), self.get_w_u_bnd(), self.get_res_freq())
            else:
                pass

        print("DEBUG: lower_bound={}={}, upper_bound={}={}, frequency={}={}".format(self.w_l_bnd, lower_bound, self.w_u_bnd, upper_bound, self.get_res_freq(), frequency))

    def calc_z(self):
        zs = np.zeros_like(self.f_sweep)
        if series:
            for z, w in zip(zs, self.f_sweep):
                z = 1.0/(complex(0, w*C)) + complex(0, w*L)

        elif not series:
            for z, w in zip(zs, self.f_sweep):
                z = 1.0/((complex(0, w*C)) + 1.0/complex(0, w*L))

            return zs

    def calc_s11(self):
        gs = np.zeros_like(self.f_sweep)
        for z, g in zip(calc_z(), gs):
            g = (z_in - (z_in + z))/(z_in + (z_in + z))

        return gs

    def get_slopes(gammas):
        # Calculates the discrete derivative of S11 w.r.t. frequency and returns the derivative array.
        dgs = np.diff(gammas)/step_size
        dgs = np.abs(dgs)
        dgs = dgs.append(dgs[-1])   # Just some dimension housekeeping. Duplicated and appended the last element.

        return dgs

    def find_steep(self):
        # Returns the frequency which corresponds to the steepest part of S11 (to maximize sensitivity.)
        gammas = calc_s11(self)
        slopes = get_slopes(gammas)
        max_slope = np.max(slopes)
        max_ind = np.argmax(slopes)

        if max_slope != slopes[max_ind]:
            print("ERROR! max_slope != slopes[max_ind]!")

        return {"frequency": self.f_sweep[max_ind],
                "derivative": max_slope}

    def plot(self, ys = None):
        # Plots passed ys vs the frequencies specified in f_sweep.
        xs = self.get_freq()

        plt.figure()
        plt.plot(xs, ys, 'r')
        plt.title('S11')
