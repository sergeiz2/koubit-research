#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from time import sleep

import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import e, hbar

import qcodes as qc
from qcodes import (Instrument)
from qcodes.utils.validators import Numbers, Arrays
from qcodes.instrument.parameter import ParameterWithSetpoints, Parameter
from qcodes.dataset.measurements import Measurement
from qcodes.dataset.plotting import plot_dataset
from qcodes.dataset.sqlite.database import initialise_or_create_database_at
from qcodes.dataset.experiment_container import load_or_create_experiment



class TotalCurrent(Parameter):
    '''
    TotalCurrent parameter of SQUID. This class calculates the
    total current in get_raw() which it overwrites from the
    Parameter class. This construction allows us to associate our
    own Parameter subclass with our instrument rather than
    calculating parameter values in the Instrument class.
    '''

    # All parameter constructors should accept **kwargs and
    # specify a name and an associated instrument, then pass
    # all these on to super().__init__
    def __init__(self, name, instrument, **kwargs):
        super().__init__(name=name, instrument=instrument, **kwargs)
        #FIXME: DEBUGGING
        print(self)
        print(name)
        print(self.root_instrument.critical_current())
        print(self.root_instrument.ext_flux())

    def get_raw(self):
        #TODO: figure out this phase thing.
        phase = np.pi/2.0
        return 2.0 * self.root_instrument.critical_current.get_latest() * np.sin(phase) * np.cos(e / hbar * self.root_instrument.ext_flux.get_latest())

class FluxAxis(Parameter):
    """
    A parameter that generates a setpoint array from start, stop and num points
    parameters.
    """
    def __init__(self, name, instrument, start, stop, numpoints, **kwargs):
        super().__init__(name=name, instrument=instrument, **kwargs)
        self._startparam = start
        self._stopparam = stop
        self._numpointsparam = numpoints

    def get_raw(self):
        return np.linspace(self._startparam(), self._stopparam(),
                              self._numpointsparam())

class TotalCurrentAxis(ParameterWithSetpoints):

    def __init__(self, name, instrument, **kwargs):
        super().__init__(name=name, instrument=instrument, **kwargs)

    def get_raw(self):
        npoints = self.root_instrument.n_points.get_latest()
        axis = np.zeroes(npoints)

        for i in range(len(axis)) :
            axis[i] = self.root_instrument.total_current()

        return axis


class SQUID(Instrument):
    """
    QCoDeS driver for the SQUID. Contains parameters critical_current,
    for the critical current of the SQUID, ext_flux for the (simulated)
    applied external flux the SQUID sees, and total_current for the
    total current that passes through the SQUID.
    """

    # All instrument constructors should accept **kwargs and
    # specify a name, then pass both these on to super().__init__
    def __init__(self, name, crit_current=1, **kwargs): #Note that critical current is set in the constructor.
        super().__init__(name, **kwargs)

        self.add_parameter('critical_current',
                           unit='A',
                           label='Critical current',
                           get_parser=float,
                           get_cmd=None,
                           set_cmd=None
                           )
        self.critical_current(crit_current) #Must be set immediately after adding the critical current parameter.

        self.add_parameter('ext_flux',
                           unit='T',
                           label='Applied external flux',
                           get_parser=float,
                           get_cmd=None,
                           set_cmd=None
                           )
        self.calibrate() #Must be done immediately after adding the external flux parameter.


        self.add_parameter('total_current',
                           unit='A',
                           label='Total current',
                           parameter_class=TotalCurrent,
                           get_parser=float,
                           set_cmd=False
                           )

        self.add_parameter('phi_start',
                           initial_value=0,
                           unit='T',
                           label='flux start',
                           vals=Numbers(0,1e3),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('phi_stop',
                           unit='T',
                           label='flux stop',
                           vals=Numbers(1,1e3),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('n_points',
                           unit='',
                           initial_value=10,
                           vals=Numbers(1,1e3),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('ext_flux_axis',
                           unit='T',
                           label='Applied External Flux',
                           parameter_class=FluxAxis,
                           start=self.phi_start,
                           stop=self.phi_stop,
                           numpoints=self.n_points,
                           vals=Arrays(shape=(self.n_points.get_latest,))
                           )

        self.add_parameter('total_current_axis',
                           unit='A',
                           label='Total Current',
                           parameter_class=TotalCurrentAxis,
                           vals=Arrays(shape=(self.n_points.get_latest,))
                           )


        if self.name is 'tempSQUID': #Only print connect message when actual SQUID connected, not when a temp one is instantiated.
            pass
        else:
            print('\n' * 5) #I got annoyed with the VISA import warning, so I'm just pushing it up.
            print('-' * 70)
            self.connect_message()
            print('-' * 70)

    def get_idn(self): #Overwritten the get id function from the instrument superclass.
        return {'vendor' : 'KOUBIT', 'model' : 'squiddy', 'serial': self.name + '-217', 'firmware' : '0.0'}

    def calibrate(self, phi=0, start=0, stop=10, npoints=1e3): #Sets current external flux to given value (0 by default)
        self.ext_flux(phi)
        self.phi_start(start)
        self.phi_stop(stop)
        self.npoints(n_points)


"""
-----------------
CREATE EXPERIMENT
-----------------
"""

db_path = os.path.join(os.getcwd(), 'squid_test.db')
initialise_or_create_database_at(db_path)
load_or_create_experiment(experiment_name='HelloSid', sample_name="no sample")


"""
-----------
MEASUREMENT
-----------
"""

sid = SQUID('SidTheSQUID', crit_current=0.04)
meas = Measurement()
meas.register_parameter(sid.ext_flux_axis)
meas.register_parameter(sid.total_current_axis)

# sweep = sid.ext_flux.sweep(0,10,1E-3)

# sweep = np.linspace(0,5,int(1E2))
# fluxes, currents = [],[]

# for phi in sweep:
#     # exp_run.add_result((sid.ext_flux, phi), (sid.total_current, sid.total_current()))
#     # data = exp_run.dataset()
#     sid.ext_flux(phi)
#     fluxes.append(sid.ext_flux())
#     currents.append(sid.total_current())

with meas.run() as save_data:
    save_data.add_result((sid.ext_flux_axis, sid.ext_flux_axis()), (sid.total_current_axis, sid.total_current_axis()))
    dataset = save_data.dataset

plot_dataset(save_data.dataset)

# plt.plot(fluxes, currents, 'b-')

# with meas.run() as exp_run:
#     next_flux = sweep.next(False)
#     while next_flux:
#         exp_run.add_result((sid.ext_flux, next_flux), (sid.total_current, sid.total_current()))

    # data = exp_run.dataset()

# plt.show()
