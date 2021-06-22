
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
