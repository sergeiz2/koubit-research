#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from ResSensitivity import *


def new_circ():
    circ = Circuit(True, 20e-9, 24.925e-15, 1000, 50, 4e9, 15e9)

def def_new_circ():
    circ = Circuit()

def calc_z():
    z_str = circ.calc_z()
    print(z_str)

def calc_s11():
    s11_str = circ.calc_z()
    print(s11_str)

def plot_ref():
    circ.plot_s11(circ.calc_s11())

#Gets slopes of |S11|
def get_slopes():
    slopes_str = circ.get_slopes(circ.calc_s11())
    print(slopes_str)

def plot_slopes():
    plt.figure()
    plt.plot(circ.get_f_sweep(), circ.get_slopes(circ.calc_s11()))
    plt.show()

def find_steep():
    s11 = circ.calc_s11()
    steep_dict = circ.find_steep(circ.get_slopes(s11), s11)
    print(steep_dict)
