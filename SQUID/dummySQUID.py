#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from time import sleep

import matplotlib.pyplot as plt
import numpy as np

import qcodes as qc
from qcodes import (
    Measurement,
    experiments,
    initialise_database,
    initialise_or_create_database_at,
    load_by_guid,
    load_by_run_spec,
    load_experiment,
    load_last_experiment,
    load_or_create_experiment,
    new_experiment,
)
from qcodes.utils.validators import Numbers, Arrays
from qcodes.dataset.plotting import plot_dataset
# from qcodes.dataset.measurements import Measurement
from qcodes.logger.logger import start_all_logging
from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import ParameterWithSetpoints, Parameter
from qcodes.tests.instrument_mocks import DummyInstrument
# from qcodes.tests.instrument_mocks import DummyInstrumentWithMeasurement
# from qcodes.dataset.sqlite.database import initialise_or_create_database_at
# from qcodes.dataset.experiment_container import load_or_create_experiment

# start_all_logging() #Turn on QCoDeS logging

station = qc.Station() #Make a new station (the experimental setup which contains all the instruments.)

class GeneratedSetPoints(Parameter):
    """
    A parameter that generates a setpoint array from start, stop and num points
    parameters.
    """
    def __init__(self, startparam, stopparam, numpointsparam, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._startparam = startparam
        self._stopparam = stopparam
        self._numpointsparam = numpointsparam

    def get_raw(self):
        return np.linspace(self._startparam(), self._stopparam(),
                              self._numpointsparam())

class DummyArray(ParameterWithSetpoints):

    def get_raw(self):
        npoints = self.root_instrument.n_points.get_latest()
        return np.random.rand(npoints)

class DummySQUID(Instrument):

    def __init__(self, name, **kwargs):

        super().__init__(name, **kwargs)

        self.add_parameter('f_start',
                           initial_value=0,
                           unit='Hz',
                           label='f start',
                           vals=Numbers(0,1e3),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('f_stop',
                           unit='Hz',
                           label='f stop',
                           vals=Numbers(1,1e3),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('n_points',
                           unit='',
                           initial_value=10,
                           vals=Numbers(1,1e3),
                           get_cmd=None,
                           set_cmd=None)

        self.add_parameter('freq_axis',
                           unit='Hz',
                           label='Freq Axis',
                           parameter_class=GeneratedSetPoints,
                           startparam=self.f_start,
                           stopparam=self.f_stop,
                           numpointsparam=self.n_points,
                           vals=Arrays(shape=(self.n_points.get_latest,)))

        self.add_parameter('spectrum',
                           unit='dBm',
                           setpoints=(self.freq_axis,),
                           label='Spectrum',
                           parameter_class=DummyArray,
                           vals=Arrays(shape=(self.n_points.get_latest,)))
