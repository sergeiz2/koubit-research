#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import numpy as np

import qcodes as qc
from qcodes import Instrument
from qcodes.instrument.parameter import Parameter
from qcodes.utils.validators import ComplexNumbers

class BuiltinImp(Parameter):
    '''
    Parameter calculates the built-in impedance of the circuit (without the black box) in its get_raw() method.
    '''
    w = None

    def __init__(self, name, instrument, **kwargs):
        super().__init__(name=name, instrument=instrument, **kwargs)
        self.set_supply_freq(self.root_instrument.supply_freq())

    def set_supply_freq(self, supply_freq):  # These shenanigans are so that I can just call this function again later during the ZeroDivisionError handling in get_raw().
        global w                             # w for \omega
        w = supply_freq

    def get_raw(self, **kwargs):
        L = self.root_instrument.builtin_ind()
        C = self.root_instrument.builtin_cap()
        self.set_supply_freq(self.root_instrument.supply_freq())

        global w
        try:
            return ((1.0 /  complex(0, w*L)) + complex(0, w*C))**-1
        except ZeroDivisionError:
            print("Frequency was zero, but this results in division by zero. It will be reset to 1E-12.")
            w = 1E-12
            return ((1.0 /  complex(0, w*L)) + complex(0, w*C))**-1


class TotalImp(Parameter):
    '''
    Parameter calculates the total impedance of the circuit (including the impedance specified for the "black box")
    '''
    def __init__(self, name, instrument, **kwargs):
        super().__init__(name=name, instrument=instrument, **kwargs)

    def get_raw(self):
        Z_0 = self.root_instrument.builtin_imp()
        Z_e = self.root_instrument.ext_imp()

        return (Z_0 * Z_e) / (Z_0 + Z_e)

class ReflectionCoeff(Parameter):
    '''
    Parameter calculates the reflection coefficient of the circuit at a certain frequency.

    The amplitude of the reflected voltage wave normalized to the amplitude
    of the incident voltage wave is defined as the voltage reflection
    coefficient. If I'm interpreting this correctly, the source has no
    impedance and our Z_in is calculated from the built-in circuit impedance.
    Consequently, Z_circ is the total circuit impedance. The reflection coefficient
    is given by \Gamma(\omega) = \frac{Z_{in} - Z_{circ}}{Z_{in} + Z_{circ}}.
    '''

    def __init__(self, name, instrument, **kwargs):
        super().__init__(name=name, instrument=instrument, **kwargs)

    def get_raw(self):
        Z_in = self.root_instrument.input_imp()
        Z_circ = self.root_instrument.total_imp()
        return (Z_circ - Z_in) / (Z_circ + Z_in)

class ResonantFreq(Parameter):
    '''
    Parameter calculates the resonant frequency of the LC circuit without the "black box".
    '''

    def __init__(self, name, instrument, **kwargs):
        super().__init__(name=name, instrument=instrument, **kwargs)

    def get_raw(self):
        L = self.root_instrument.builtin_ind()
        C = self.root_instrument.builtin_cap()
        return 1/np.sqrt(L*C)

class Circuit(Instrument):
    """
    QCoDeS driver for the circuit.
    """

    def __init__(self, name, ext_imp=complex(200.0, 100.0), potential=1E-2, input_imp=100.0, builtin_ind=46.1E-9, builtin_cap=2.61E-12, **kwargs):
        super().__init__(name, **kwargs)

        self.add_parameter('potential',  # Max amplitude of potential waveform at frequency (below)
                           unit='Volt',
                           get_parser=float,
                           get_cmd=None,
                           set_cmd=None
                           )

        self.add_parameter('supply_freq',  # Frequency supplied to circuit
                           unit='Hertz',  # ATTN: SI Unit. Typically in GHz range
                           initial_value=0,
                           get_parser=float,
                           get_cmd=None,
                           set_cmd=None
                           )

        self.add_parameter('input_imp',  # Input impedance
                           unit='Ohm',
                           get_parser=float,
                           get_cmd=None,
                           set_cmd=None
                           )

        self.add_parameter('builtin_ind',  # Built-in circuit inductance (without the "black box")
                           unit='Henry', # ATTN: SI Unit. Typical inductor values in NH range
                           get_parser=float,
                           get_cmd=None,
                           set_cmd=None
                           )

        self.add_parameter('builtin_cap',  # Built-in circuit capacitance (without the "black box")
                           unit='Farad',  # ATTN: SI Unit. Typical inductor values in pF range
                           get_parser=float,
                           get_cmd=None,
                           set_cmd=None
                           )

        self.add_parameter('builtin_imp',  # Built-in circuit impedance (without the "black box")
                           unit='Ohm',
                           parameter_class=BuiltinImp,
                           get_cmd=None,
                           set_cmd=None,
                           vals=ComplexNumbers()  # Must be complex
                           )

        self.add_parameter('ext_imp',  # Impedance of our "black box"
                           unit='Ohm',
                           get_cmd=None,
                           set_cmd=None,
                           vals=ComplexNumbers()  # Must be complex
                           )

        self.add_parameter('total_imp',  # Total impedance of entire circuit with all components
                           unit='Ohm',
                           parameter_class=TotalImp,
                           get_cmd=None,
                           set_cmd=None,
                           vals=ComplexNumbers()  # Must be complex
                            )

        self.add_parameter('res_freq',  # Resonant frequency of the LC circuit (sans black box)
                           unit='Hertz',
                           parameter_class=ResonantFreq,
                           get_cmd=None,
                           set_cmd=None,
                           get_parser=float
                           )

        self.add_parameter('ref_coeff',  # Reflection coefficient (see parameter class for more info)
                           unit='Units (dimensionless)',
                           parameter_class=ReflectionCoeff,
                           get_cmd=None,
                           set_cmd=None,
                           vals=ComplexNumbers()
                           )

        self.set_values(Z=ext_imp, V=potential, Z_in=input_imp, L=builtin_ind, C=builtin_cap) #Properly sets default input and baked-in parameters.
        self.connect_message()

    def get_idn(self): #Overwritten the get id function from the instrument superclass.
        return {'vendor' : 'KOUBIT', 'model' : 'Elsie', 'serial': self.name + '-217', 'firmware' : '0.0'}

    def set_values(self, Z, V, Z_in, L, C):
        self.ext_imp(Z)
        self.potential(V)
        self.input_imp(Z_in)
        self.builtin_ind(L)
        self.builtin_cap(C)
        self.builtin_ind()      #This is important, it sets the value for builtin_ind so that it's not None when the experiment is run.

# """
# -----------------
# CREATE EXPERIMENT
# -----------------
# """

# '''
# Here we initialize a database for the experiment we're about to be running.
# '''
# db_path = os.path.join(os.getcwd(), 'LC_test.db')
# initialise_or_create_database_at(db_path)
# load_or_create_experiment(experiment_name='HelloElsie', sample_name="no sample")


# """
# -----------
# MEASUREMENT
# -----------
# """
# # TODO: Description
# '''
# Here we create a Circuit object and ...
# '''

# def gen_freqs(circ, ctr=None, rng=1E-3):  # Frequy spelling...
#     if ctr == None:
#         center = circ.res_freq()  # 'center' because it's where the features we want to see on the graph are.
#         print(circ.res_freq())
#     else:
#         center = ctr

#     freqs = np.linspace(center - rng, center + rng, int(1E5))

#     return freqs


# def gen_imps(cir, freqs):                   # No, impedances not monkeys.
#     imps = np.zeros_like(freqs)

#     for ind, freq in enumerate(freqs):
#         circ.supply_freq(freq)
#         imps[ind] = np.absolute(circ.builtin_imp())  # Note the absolute value.

#     return imps


# def gen_refs(circ, freqs):                   # refs, i.e reflection coefficients.
#     refs = np.zeros_like(freqs)

#     for ind, freq in enumerate(freqs):
#         circ.supply_freq(freq)
#         refs[ind] = np.absolute(circ.ref_coeff())  # Note the absolute value.

#     return refs

# def find_refs_ctr(circ, freqs, refs):  # This method is necessary to find the center of the reflection coefficient graph.
#     center = 0.0
#     end_ref = refs[-1]
#     rng = 0.0

#     if end_ref > .9999999999:
#         center = freqs[int(len(refs)-1)]
#         rng = freqs[int(len(refs)-1)]
#     else:
#         new_freqs = gen_freqs(circ, ctr=freqs[-1], rng=freqs[-1])
#         new_refs = gen_refs(circ, new_freqs)
#         center = find_refs_ctr(circ, new_freqs, new_refs)[0]

#     return (center, rng)


# circ = Circuit('test')
# # circ = Circuit('test2', )
# x1 = gen_freqs(circ)
# y1 = gen_imps(circ, x1)

# refs_ctr = find_refs_ctr(circ, x1, y1)[0]
# refs_rng = find_refs_ctr(circ, x1, y1)[1]
# x2 = gen_freqs(circ, refs_ctr, refs_rng)
# y2 = gen_refs(circ, x2)

# plt.figure()
# plt.plot(x1, y1, 'b')
# plt.title('imps test')

# plt.figure()
# plt.plot(x2, y2, 'r')
# plt.title('refs test')

# fig, axs = plt.subplots(2, sharex=True)
# axs[0].plot(x1, y1, 'b')
# axs[1].plot(x2, y2, 'r')

# plt.show()


#  LocalWords:  inductor
