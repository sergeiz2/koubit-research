#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import numpy as np
# from numpy import diff

L_l_bnd = 1*10e-9               #Inductance lower bound
L_u_bnd = 100*10e-9             #Inductance upper bound
L_step = 1*10e-9
C_l_bnd = 1*10e-15              #Capacitance lower bound
C_u_bnd = 100*10e-15            #Capacitance upper bound
C_step = 1*10e-15
w_l_bnd = None                  #Frequency sweep lower bound (Hz)
w_u_bnd = None                  #Frequency sweep upper bound (Hz)

def find_ideal_C(circ, test_caps=np.arange(C_l_bnd, C_u_bnd, C_step)):
    Cs = np.arange(C_l_bnd, C_u_bnd, C_step)
    is_series = circ.get_series()
    ind = circ.get_L

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


#FIXME: Idk if this center thing is necessary at all.
# def find_ideal_C(circ, test_caps=np.arange(C_l_bnd, C_u_bnd, C_step)):
#     Cs = np.arange(C_l_bnd, C_u_bnd, C_step)
#     is_series = circ.get_series()
#     ind = circ.get_L

#     circ_l_bnd = Circuit(series=is_series, L=ind, C=C_l_bnd)
#     refs_l_bnd = circ_l_bnd.calc_s11()
#     steep_l_bnd = circ_l_bnd.find_steep(refs_l_bnd)

#     circ_ctr = circ
#     refs_ctr = circ_r_bnd.calc_s11()
#     steep_ctr = circ_r_bnd.find_steep(refs_r_bnd)

#     circ_r_bnd = Circuit(series=is_series, L=ind, C=C_r_bnd)
#     refs_r_bnd = circ_r_bnd.calc_s11()
#     steep_r_bnd = circ_r_bnd.find_steep(refs_r_bnd)

#     if steep_l_bnd.get("derivative") > steep_ctr.get("derivative") and steep_ctr.get("derivative") < steep_r_bnd.get("derivative"):
#         new_ctr_ind = (C_u_bnd - C_l_bnd)/(2 * C_step)
#         find_ideal_C(circ=Circuit(series=is_series, L=ind, C=, test_caps=np.arange(C_l_bnd, ))
#     elif steep_l_bnd.get("derivative") < steep_ctr.get("derivative") and steep_ctr.get("derivative") > steep_r_bnd.get("derivative"):
#     elif steep_l_bnd.get("derivative") > steep_ctr.get("derivative") and steep_ctr.get("derivative") > steep_r_bnd.get("derivative"):
#         if steep_l_bnd.get("derivative") > steep_r_bnd.get("derivative"):
#         else:


class Circuit():
    series = None               #True for series circuit, false for parallel.
    L = None                    #Inductance (H)
    C = None                    #Capacitance (F)
    z_in = None                 #Input impedance (Ohm)
    w_r = None                  #Resonant frequency (Hz)
    step_size = None            #Frequency sweep step size (Hz)
    f_sweep = None              #Frequency sweep (Hz)
    s11 = None                  #S11 reflection coefficients.

    def __init__(self, series=None, L=None, C=None, stp_size=1e-2, w_l_bnd=4*10e9, w_u_bnd=8*10e9):
        set_LC(L, C)
        set_par_or_ser(series)
        set_freq_sweep(stp_size)
        set_res_freq(L, C)

        check_in_bounds(w_l_bnd, w_u_bnd, w_r)

    def set_par_or_ser(ser=None):
        if ser == None:
            par_or_ser = input("Is this a parallel or a series circuit? (P/S):")

            if par_or_ser == "P" or par_or_ser == "p":
                series = False

            elif par_or_ser == "S" or par_or_ser == "s":
                series = True

            else:
                print("Invalid selection!")
                set_par_or_ser()

        else:
            series = ser

    def set_LC(ind, cap):
        if not(ind or cap):
            L = input("Please input starting inductor value (H):")
            C = input("Please input starting capacitor value (in F):")
            #NOTE: subdivisions smaller than nH and fF will probably break things.

        else:
            L = ind
            C = cap

    def get_L():
        return L

    def get_C():
        return C

    def get_series():
        return series

    def set_res_freq(inductance, capacitance):
        w_r = 1/(np.sqrt(L*C))
        print("The circuit will resonate at a frequency of {} GHz".format(w/10e9))

    def check_in_bounds(lower_bound, upper_bound, freqency):

        if lower_bound <= frequency <= upper_bound:
            pass
        else:
            print("The resonant frequency is not within your bounds. Do you want to change it?")
            yes_or_no = input("Y/N:")

            if yes_or_no == "Y" or yes_or_no == "y":
                set_LC()
            else:
                pass

    def set_freq_sweep(step):
        w_l_bnd = input("Please enter the lower bound of your frequency sweep (Hz)") #Lower bound frequency sweep
        w_u_bnd = input("Please enter the upper bound of your frequency sweep (Hz)") #Upper bound frequency sweep

        f_sweep = np.arange(w_l_bnd, w_u_bnd, step)

    def calc_z():
        zs = np.zeros_like(f_sweep)
        if series:
            for z, w in zip(zs, f_sweep):
                z = 1.0/(complex(0, w*C)) + complex(0, w*L)

        elif not series:
            for z, w in zip(zs, f_sweep):
                z = 1.0/((complex(0, w*C)) + 1.0/complex(0, w*L))

            return zs

    def calc_s11():
        gs = np.zeros_like(f_sweep)
        for z, g in zip(calc_z(), gs):
            g = (z_in - (z_in + z))/(z_in + (z_in + z))

        return gs

    def get_slopes(gammas):
        # Calculates the discrete derivative of S11 w.r.t. frequency and returns the derivative array.
        dgs = np.diff(gammas)/step_size
        dgs = np.abs(dgs)
        dgs = dgs.append(dgs[-1])   # Just some dimension housekeeping. Duplicated and appended the last element.

        return dgs

    def find_steep(gammas=calc_s11()):
        # Returns the frequency which corresponds to the steepest part of S11 (to maximize sensitivity.)
        slopes = get_slopes(gammas)
        max_slope = np.max(slopes)
        max_ind = np.argmax(slopes)

        if max_slope != slopes[max_ind]:
            print("ERROR! max_slope != slopes[max_ind]!")

        return {"frequency": f_sweep[max_ind],
                "derivative": max_slope}



#class BuiltinImp(Parameter):
#    '''
#    Parameter calculates the built-in impedance of the circuit (without the black box) in its get_raw() method.
#    '''
#    w = None
#
#    def __init__(self, name, instrument, **kwargs):
#        super().__init__(name=name, instrument=instrument, **kwargs)
#        self.set_supply_freq(self.root_instrument.supply_freq())
#
#    def set_supply_freq(self, supply_freq):  # These shenanigans are so that I can just call this function again later during the ZeroDivisionError handling in get_raw().
#        global w                             # w for \omega
#        w = supply_freq
#
#    def get_raw(self, **kwargs):
#        L = self.root_instrument.builtin_ind()
#        C = self.root_instrument.builtin_cap()
#        self.set_supply_freq(self.root_instrument.supply_freq())
#
#        global w
#        try:
#            return ((1.0 /  complex(0, w*L)) + complex(0, w*C))**-1
#        except ZeroDivisionError:
#            self.root_instrument.log.info("Frequency was zero, but this results in division by zero. It will be reset to 1E-12.")
#            w = 1E-12
#            return ((1.0 /  complex(0, w*L)) + complex(0, w*C))**-1
#
#
#class TotalImp(Parameter):
#    '''
#    Parameter calculates the total impedance of the circuit (including the impedance specified for the "black box")
#    '''
#    def __init__(self, name, instrument, **kwargs):
#        super().__init__(name=name, instrument=instrument, **kwargs)
#
#    def get_raw(self):
#        Z_0 = self.root_instrument.builtin_imp()
#        Z_e = self.root_instrument.ext_imp()
#
#        return (Z_0 * Z_e) / (Z_0 + Z_e)
#
#class ReflectionCoeff(Parameter):
#    '''
#    Parameter calculates the reflection coefficient of the circuit at a certain frequency.
#
#    The amplitude of the reflected voltage wave normalized to the amplitude
#    of the incident voltage wave is defined as the voltage reflection
#    coefficient. If I'm interpreting this correctly, the source has no
#    impedance and our Z_in is calculated from the built-in circuit impedance.
#    Consequently, Z_circ is the total circuit impedance. The reflection coefficient
#    is given by \Gamma(\omega) = \frac{Z_{in} - Z_{circ}}{Z_{in} + Z_{circ}}.
#    '''
#
#    def __init__(self, name, instrument, **kwargs):
#        super().__init__(name=name, instrument=instrument, **kwargs)
#
#    def get_raw(self):
#        Z_in = self.root_instrument.input_imp()
#        Z_circ = self.root_instrument.total_imp()
#        return (Z_circ - Z_in) / (Z_circ + Z_in)
#
#class ResonantFreq(Parameter):
#    '''
#    Parameter calculates the resonant frequency of the LC circuit without the "black box".
#    '''
#
#    def __init__(self, name, instrument, **kwargs):
#        super().__init__(name=name, instrument=instrument, **kwargs)
#
#    def get_raw(self):
#        L = self.root_instrument.builtin_ind()
#        C = self.root_instrument.builtin_cap()
#        return 1/np.sqrt(L*C)
#
#class Circuit(Instrument):
#    """
#    QCoDeS driver for the circuit.
#    """
#
#    def __init__(self, name, ext_imp=complex(200.0, 100.0), potential=1E-2, input_imp=100.0, builtin_ind=46.1E-9, builtin_cap=2.61E-12, **kwargs):
#        super().__init__(name, **kwargs)
#
#        self.add_parameter('potential',  # Max amplitude of potential waveform at frequency (below)
#                           unit='Volt',
#                           get_parser=float,
#                           get_cmd=None,
#                           set_cmd=None
#                           )
#
#        self.add_parameter('supply_freq',  # Frequency supplied to circuit
#                           unit='Hertz',  # ATTN: SI Unit. Typically in GHz range
#                           initial_value=0,
#                           get_parser=float,
#                           get_cmd=None,
#                           set_cmd=None
#                           )
#
#        self.add_parameter('input_imp',  # Input impedance
#                           unit='Ohm',
#                           get_parser=float,
#                           get_cmd=None,
#                           set_cmd=None
#                           )
#
#        self.add_parameter('builtin_ind',  # Built-in circuit inductance (without the "black box")
#                           unit='Henry', # ATTN: SI Unit. Typical inductor values in NH range
#                           get_parser=float,
#                           get_cmd=None,
#                           set_cmd=None
#                           )
#
#        self.add_parameter('builtin_cap',  # Built-in circuit capacitance (without the "black box")
#                           unit='Farad',  # ATTN: SI Unit. Typical inductor values in pF range
#                           get_parser=float,
#                           get_cmd=None,
#                           set_cmd=None
#                           )
#
#        self.add_parameter('builtin_imp',  # Built-in circuit impedance (without the "black box")
#                           unit='Ohm',
#                           parameter_class=BuiltinImp,
#                           get_cmd=None,
#                           set_cmd=None,
#                           vals=ComplexNumbers()  # Must be complex
#                           )
#
#        self.add_parameter('ext_imp',  # Impedance of our "black box"
#                           unit='Ohm',
#                           get_cmd=None,
#                           set_cmd=None,
#                           vals=ComplexNumbers()  # Must be complex
#                           )
#
#        self.add_parameter('total_imp',  # Total impedance of entire circuit with all components
#                           unit='Ohm',
#                           parameter_class=TotalImp,
#                           get_cmd=None,
#                           set_cmd=None,
#                           vals=ComplexNumbers()  # Must be complex
#                            )
#
#        self.add_parameter('res_freq',  # Resonant frequency of the LC circuit (sans black box)
#                           unit='Hertz',
#                           parameter_class=ResonantFreq,
#                           get_cmd=None,
#                           set_cmd=None,
#                           get_parser=float
#                           )
#
#        self.add_parameter('ref_coeff',  # Reflection coefficient (see parameter class for more info)
#                           unit='Units (dimensionless)',
#                           parameter_class=ReflectionCoeff,
#                           get_cmd=None,
#                           set_cmd=None,
#                           vals=ComplexNumbers()
#                           )
#
#        self.set_values(Z=ext_imp, V=potential, Z_in=input_imp, L=builtin_ind, C=builtin_cap) #Properly sets default input and baked-in parameters.
#        self.connect_message()
#
#    def get_idn(self): #Overwritten the get id function from the instrument superclass.
#        return {'vendor' : 'KOUBIT', 'model' : 'Elsie', 'serial': self.name + '-217', 'ResFreq' : self.res_freq()}
#
#    def connect_message(self, idn_param: str = 'IDN',
#                        begin_time: Optional[float] = None) -> None:
#        """
#        Overwritten from qcodes.instrument.base.
#        Print a standard message on initial connection to an instrument.
#
#        Args:
#            idn_param: Name of parameter that returns ID dict.
#                Default ``IDN``.
#            begin_time: ``time.time()`` when init started.
#                Default is ``self._t0``, set at start of ``Instrument.__init__``.
#        """
#        # start with an empty dict, just in case an instrument doesn't
#        # heed our request to return all 4 fields.
#        idn = {'vendor': None, 'model': None,
#               'serial': None, 'ResFreq': None}
#        idn.update(self.get(idn_param))
#        t = time.time() - (begin_time or self._t0)
#
#        con_msg = ('Connected to: {vendor} {model} '
#                   '(serial:{serial}, Resonant Frequency:{ResFreq}) '
#                   'in {t:.2f}s'.format(t=t, **idn))
#        print(con_msg)
#        self.log.info(f"Connected to instrument: {idn}")
#
#    def set_values(self, Z, V, Z_in, L, C):
#        self.ext_imp(Z)
#        self.potential(V)
#        self.input_imp(Z_in)
#        self.builtin_ind(L)
#        self.builtin_cap(C)
#        self.builtin_ind()      #This is important, it sets the value for builtin_ind so that it's not None when the experiment is run.
#
##  LocalWords:  inductor
