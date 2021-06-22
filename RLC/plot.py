#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

import numpy as np
import matplotlib.pyplot as plt

import qcodes as qc
from qcodes.dataset.sqlite.database import initialise_or_create_database_at
from qcodes.dataset.experiment_container import load_or_create_experiment

import RLC
from RLC import Circuit


'''
-----------------
HELPER METHODS
-----------------
Just a few helper methods for plotting.
---------------------------------------
'''

def gen_freqs(circ, ctr=None, rng=1E-3):  # Frequy spelling...
    if ctr == None:
        center = circ.res_freq()  # 'center' because it's where the features we want to see on the graph are.
    else:
        center = ctr

    freqs = np.linspace(center - rng, center + rng, int(1E5))

    return freqs


def gen_imps(cir, freqs):                   # No, impedances not monkeys.
    imps = np.zeros_like(freqs)

    for ind, freq in enumerate(freqs):
        circ.supply_freq(freq)
        imps[ind] = np.absolute(circ.builtin_imp())  # Note the absolute value.

    return imps


def gen_refs(circ, freqs):                   # refs, i.e reflection coefficients.
    refs = np.zeros_like(freqs)

    for ind, freq in enumerate(freqs):
        circ.supply_freq(freq)
        refs[ind] = np.absolute(circ.ref_coeff())  # Note the absolute value.

    return refs

def find_refs_ctr(circ, freqs, refs):  # This method is necessary to find the center of the reflection coefficient graph.
    center = 0.0
    end_ref = refs[-1]
    rng = 0.0

    if end_ref > .9999999999:
        center = freqs[int(len(refs)-1)]
        rng = freqs[int(len(refs)-1)]
    else:
        new_freqs = gen_freqs(circ, ctr=freqs[-1], rng=freqs[-1])
        new_refs = gen_refs(circ, new_freqs)
        center = find_refs_ctr(circ, new_freqs, new_refs)[0]

    return (center, rng)


'''
---------------------
INITIALIZE EXPERIMENT
---------------------
Here we initialize a database for the experiment we're about to be running.
---------------------------------------
'''

db_path = os.path.join(os.getcwd(), 'LC_test.db')
initialise_or_create_database_at(db_path)
load_or_create_experiment(experiment_name='HelloElsie', sample_name="no sample")


'''
--------
PLOTTING
--------
Actual plotting happens here!
---------------------------------------
'''


circ = Circuit('elsie')
x1 = gen_freqs(circ)
y1 = gen_imps(circ, x1)

refs_ctr = find_refs_ctr(circ, x1, y1)[0]
refs_rng = find_refs_ctr(circ, x1, y1)[1]
x2 = gen_freqs(circ, refs_ctr, refs_rng)
y2 = gen_refs(circ, x2)

plt.figure()
plt.plot(x1, y1, 'b')
plt.title('Impedances')

plt.figure()
plt.plot(x2, y2, 'r')
plt.title('Reflection Coefficients')

# fig, axs = plt.subplots(2, sharex=True)
# axs[0].plot(x1, y1, 'b')
# axs[1].plot(x2, y2, 'r')

plt.show()
