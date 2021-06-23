#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import numpy as np

import qcodes as qc
from qcodes import Instrument
from qcodes.instrument.parameter import Parameter
from qcodes.utils.validators import ComplexNumbers

from typing import Optional

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
            self.root_instrument.log.info("Frequency was zero, but this results in division by zero. It will be reset to 1E-12.")
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
        return {'vendor' : 'KOUBIT', 'model' : 'Elsie', 'serial': self.name + '-217', 'ResFreq' : self.res_freq()}

    def connect_message(self, idn_param: str = 'IDN',
                        begin_time: Optional[float] = None) -> None:
        """
        Overwritten from qcodes.instrument.base.
        Print a standard message on initial connection to an instrument.

        Args:
            idn_param: Name of parameter that returns ID dict.
                Default ``IDN``.
            begin_time: ``time.time()`` when init started.
                Default is ``self._t0``, set at start of ``Instrument.__init__``.
        """
        # start with an empty dict, just in case an instrument doesn't
        # heed our request to return all 4 fields.
        idn = {'vendor': None, 'model': None,
               'serial': None, 'ResFreq': None}
        idn.update(self.get(idn_param))
        t = time.time() - (begin_time or self._t0)

        con_msg = ('Connected to: {vendor} {model} '
                   '(serial:{serial}, Resonant Frequency:{ResFreq}) '
                   'in {t:.2f}s'.format(t=t, **idn))
        print(con_msg)
        self.log.info(f"Connected to instrument: {idn}")

    def set_values(self, Z, V, Z_in, L, C):
        self.ext_imp(Z)
        self.potential(V)
        self.input_imp(Z_in)
        self.builtin_ind(L)
        self.builtin_cap(C)
        self.builtin_ind()      #This is important, it sets the value for builtin_ind so that it's not None when the experiment is run.

#  LocalWords:  inductor
