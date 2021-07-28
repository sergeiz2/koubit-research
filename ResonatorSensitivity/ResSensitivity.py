#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import numpy as np
import matplotlib.pyplot as plt

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
        self.set_w_l_bnd(w_l_bnd)
        self.set_w_u_bnd(w_u_bnd)
        self.set_LC(L, C)
        self.set_Z_in(z_in)
        self.set_par_or_ser(series)
        self.set_stp_size(stp_size)
        self.set_f_sweep(self.get_stp_size())
        #FIXME: Hackish solution for only running check_in_bounds() when user inputs values (see FIXME in set_LC())
        self.calc_res_freq()
        # self.check_in_bounds(self.get_w_l_bnd(), self.get_w_u_bnd(), self.get_res_freq())

    def __str__(self):
        dict = {'series': 'Yes' if self.get_is_series() else 'No',
                'L': self.get_L(),
                'C': self.get_C(),
                'frequencies': '{} - {} Hz'.format(self.get_w_l_bnd(), self.get_w_u_bnd()),
                'step_size': '{} Hz'.format(self.get_stp_size())}

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
            self.is_series = ser

    #TODO: Logic does not account for changing only one of two
    def set_LC(self, ind=None, cap=None):
        if not(ind or cap):
            #NOTE: subdivisions smaller than nH and fF will probably break things.
            if not(ind):
                self.L = float(input("Please input an inductor value (H):"))
            if not(cap):
                self.C = float(input("Please input a capacitor value (in F):"))

            #FIXME: Hackish solution for only running check_in_bounds() when user inputs values
            self.calc_res_freq()
            self.check_in_bounds(self.get_w_l_bnd(), self.get_w_u_bnd(), self.get_res_freq())

        else:
            self.L = ind
            self.C = cap

        # print("DEBUG: L={}, C={}".format(self.get_L(), self.get_C()))

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

        # print("DEBUG: w_r={}".format(self.get_res_freq()))

    def set_f_sweep(self, step):
        freq_sweep = np.arange(self.get_w_l_bnd(), self.get_w_u_bnd(), step)
        self.f_sweep = freq_sweep
        self.w_sweep = freq_sweep*2*np.pi
        # print("DEBUG: f_sweep={}".format(self.get_f_sweep()))

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

        # print("DEBUG: lower_bound={}={}, upper_bound={}={}, frequency={}={}".format(self.w_l_bnd, lower_bound, self.w_u_bnd, upper_bound, self.get_res_freq(), frequency))

    def calc_z(self):
        series = self.get_is_series()
        ws = self.get_w_sweep()
        zs = np.zeros_like(ws, dtype=np.complex128)
        C = self.get_C()
        L = self.get_L()

        if series:
            Z_C = np.complex128(1.0j/(ws*C))
            Z_L = np.complex128(1.0j*ws*L)
            zs = np.sqrt(np.square(Z_L + Z_C))
            # print("DEBUG: series")

        elif not(series):
            zs = np.complex128(-1.0j)*(L/C)/(ws*L - (1.0/(ws*C)) )
            # print("DEBUG: not series")

        return zs

    def calc_s11(self):
        gs = np.zeros_like(self.get_w_sweep())
        zs = self.calc_z()
        z_in = self.get_Z_in()

        gs = (z_in - (z_in + zs))/(z_in + (z_in + zs))

        return gs

    def get_slopes(self, gammas=None):
        # Calculates the discrete derivative of S11 w.r.t. frequency and returns the absolute value of derivative array.
        dgs = np.diff(gammas)/self.get_stp_size()
        dgs = np.abs(dgs)                          # We only care about the magnitude of the slope.
        dgs = np.append(dgs, dgs[-1])  # Just some dimension housekeeping. Duplicated and appended the last element.

        return dgs

    def find_steep(self, slopes=None, gammas=None):
        # Returns the frequency which corresponds to the steepest part of S11 (to maximize sensitivity.)
        freqs = self.get_w_sweep()
        max_slope = np.max(slopes)
        max_ind = np.argmax(slopes)
        max_freq = freqs[max_ind]
        step = self.get_stp_size()
        find_steep_dict = None

        #FIXME: This is not robust. It assumes a (relatively) small step size.
        if step != 1.0:
            subc_is_series = self.get_is_series()
            subc_L = self.get_L()
            subc_C = self.get_C()
            subc_z_in = self.get_Z_in()
            subc_w_l_bnd = max_freq - step
            subc_w_u_bnd = max_freq + step
            step = 1.0

            circ = Circuit(subc_is_series, subc_L, subc_C, step, subc_z_in, subc_w_l_bnd, subc_w_u_bnd)
            # print('DEBUG: ' + circ.__str__())
            subc_gammas = circ.calc_s11()
            # print('DEBUG: subc_gammas=' + str(subc_gammas))
            subc_slopes = circ.get_slopes(subc_gammas)
            # print('DEBUG: subc_slopes=' + str(subc_slopes))
            find_steep_dict = circ.find_steep(subc_slopes, subc_gammas)

        if max_slope != slopes[max_ind]:
            print("DEBUG: max_slope != slopes[max_ind]")

        find_steep_dict = {"frequency": max_freq,
                           "derivative": max_slope}

        return find_steep_dict

    def plot_s11(self, gammas=None):
        # Plots passed gammas vs the frequencies specified in f_sweep.
        xs = self.get_f_sweep()
        phase = np.angle(gammas, deg=True)
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
