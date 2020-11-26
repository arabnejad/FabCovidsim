"""
==============================================================================
FULL DIMENSION-ADAPTIVE COVIDSIM CAMPAIGN IN A SINGLE SCRIPT
==============================================================================
"""
import numpy as np
import easyvvuq as uq
import chaospy as cp
import os
import json
import matplotlib.pyplot as plt
import fabsim3_cmd_api as fab
from custom import CustomEncoder

home = os.path.abspath(os.path.dirname(__file__))
output_columns = ["cumDeath"]
work_dir = '/home/wouter/VECMA/Campaigns'
config = 'PC_CI_HQ_SD_suppress_campaign_all'
ID = '_all_interp'
method='surplus'

#set to True if starting a new campaign
init = False
if init:
    # Set up a fresh campaign
    campaign = uq.Campaign(name='covid', work_dir=work_dir)
    
    # Define parameter space for the cannonsim app
    params = json.load(open(home + '/../templates_campaign_full1/params.json'))
    
    #manually add mortality factor, which parameterizes CriticalToDeath_icdf
    #and SARIToDeath_icdf
    params["Mortality_factor"] = {"default":1, "type": "float"}
    
    #manually add Proportion_symptomatic to seed the array with a uniform value
    params["Proportion_symptomatic"] = {"default": 0.66, "type": "float"}
    
    #manually add Relative_spatial_contact_rates_by_age_power, used to parameterize
    #Relative_spatial_contact_rates_by_age_array
    params["Relative_spatial_contact_rates_by_age_power"] = {"default": 1, "type": "float"}
    
    # Modify the random seeds manually
    # params['Random_seeds0']['default'] = 98798250
    # params['Random_seeds1']['default'] = 729201
    # params['Random_seeds2']['default'] = 17389301
    # params['Random_seeds3']['default'] = 4797332
    
    # Create an encoder and decoder
    directory_tree = {'param_files': None}
    
    multiencoder_p_PC_CI_HQ_SD = uq.encoders.MultiEncoder(
        uq.encoders.DirectoryBuilder(tree=directory_tree),
        uq.encoders.JinjaEncoder(         
            template_fname=home + '/../templates_campaign_full1/p_PC_CI_HQ_SD.txt',
            target_filename='param_files/p_PC_CI_HQ_SD.txt'),
        CustomEncoder(
            template_fname=home + '/../templates_campaign_full1/preGB_R0=2.0.txt',
            target_filename='param_files/preGB_R0=2.0.txt'),    
        uq.encoders.JinjaEncoder(
            template_fname=home + '/../templates_campaign_full1/p_seeds.txt',
            target_filename='param_files/p_seeds.txt')
    )
    
    decoder = uq.decoders.SimpleCSV(
        target_filename='output_dir/United_Kingdom_PC_CI_HQ_SD_R0=2.4.avNE.severity.xls', 
        output_columns=output_columns, header=0, delimiter='\t')
    
    collater = uq.collate.AggregateHDF5()
    
    # Add the app
    campaign.add_app(name=config,
                     params=params,
                     encoder=multiencoder_p_PC_CI_HQ_SD,
                     collater=collater,
                     decoder=decoder)
    # Set the active app 
    campaign.set_app(config)
    
    #########################
    # parameters to vary    #
    # place types           #
    # ----------------------#
    # 0 = elementary school #
    # 1 = high school       #
    # 2 = university        #
    # 3 = workplaces        #
    #########################
    
    vary = {
        ###########################
        # Intervention parameters #
        ###########################
        "Relative_household_contact_rate_after_closure": cp.Uniform(1.5*0.8, 1.5*1.2),
        "Relative_spatial_contact_rate_after_closure": cp.Uniform(1.25*0.8, 1.25*1.2), #comment
        "Relative_household_contact_rate_after_quarantine": cp.Uniform(2.0*0.8, 2.0*1.2), #comment
        "Residual_spatial_contacts_after_household_quarantine": cp.Uniform(0.25*0.8, 0.25*1.2), #comment
        "Household_level_compliance_with_quarantine": cp.Uniform(0.5, 0.9),
        "Individual_level_compliance_with_quarantine": cp.Uniform(0.9, 1.0),  #comment
        "Proportion_of_detected_cases_isolated":cp.Uniform(0.6, 0.8),  #comment
        "Residual_contacts_after_case_isolation":cp.Uniform(0.25*0.8, 0.25*1.2),  #comment
        "Relative_household_contact_rate_given_social_distancing":cp.Uniform(1.1, 1.25*1.2),  #comment
        "Relative_spatial_contact_rate_given_social_distancing":cp.Uniform(0.15, 0.35),
        "Delay_to_start_household_quarantine":cp.DiscreteUniform(1, 3),
        "Length_of_time_households_are_quarantined":cp.DiscreteUniform(12, 16),
        "Delay_to_start_case_isolation":cp.DiscreteUniform(1, 3),
        "Duration_of_case_isolation":cp.DiscreteUniform(5, 9),
        ######################
        # Disease parameters #
        ######################
        "Symptomatic_infectiousness_relative_to_asymptomatic": cp.Uniform(1,2),
        "Proportion_symptomatic": cp.Uniform(0.4,0.8),
        "Latent_period": cp.Uniform(3,6),
        "Mortality_factor": cp.Uniform(0.8,1.2),
        # "Reproduction_number": cp.Uniform(2,2.7),
        "Infectious_period": cp.Uniform(11.5, 15.6),
        "Household_attack_rate": cp.Uniform(0.1, 0.19),
        "Household_transmission_denominator_power": cp.Uniform(0.7, 0.9),
        "Delay_from_end_of_latent_period_to_start_of_symptoms": cp.Uniform(0, 1.5),
        "Relative_transmission_rates_for_place_types0": cp.Uniform(0.08, 0.15),
        "Relative_transmission_rates_for_place_types1": cp.Uniform(0.08, 0.15),
        "Relative_transmission_rates_for_place_types2": cp.Uniform(0.05, 0.1),
        "Relative_transmission_rates_for_place_types3": cp.Uniform(0.05, 0.07),
        "Relative_spatial_contact_rates_by_age_power": cp.Uniform(0.25, 4),
        ######################
        # Spatial parameters #
        ######################
        "Proportion_of_places_remaining_open_after_closure_by_place_type2": cp.Uniform(0.2, 0.3),
        "Proportion_of_places_remaining_open_after_closure_by_place_type3": cp.Uniform(0.8, 1.0),
        "Residual_place_contacts_after_household_quarantine_by_place_type0": cp.Uniform(0.2, 0.3),
        "Residual_place_contacts_after_household_quarantine_by_place_type1": cp.Uniform(0.2, 0.3),
        "Residual_place_contacts_after_household_quarantine_by_place_type2": cp.Uniform(0.2, 0.3),
        "Residual_place_contacts_after_household_quarantine_by_place_type3": cp.Uniform(0.2, 0.3),
        "Relative_place_contact_rate_given_social_distancing_by_place_type0": cp.Uniform(0.8, 1.0),
        "Relative_place_contact_rate_given_social_distancing_by_place_type1": cp.Uniform(0.8, 1.0),
        "Relative_place_contact_rate_given_social_distancing_by_place_type2": cp.Uniform(0.6, 0.9),
        "Relative_place_contact_rate_given_social_distancing_by_place_type3": cp.Uniform(0.6, 0.9),
        "Relative_rate_of_random_contacts_if_symptomatic": cp.Uniform(0.4, 0.6),
        "Relative_level_of_place_attendance_if_symptomatic0": cp.Uniform(0.2, 0.3),
        "Relative_level_of_place_attendance_if_symptomatic1": cp.Uniform(0.2, 0.3),
        "Relative_level_of_place_attendance_if_symptomatic2": cp.Uniform(0.4, 0.6),
        "Relative_level_of_place_attendance_if_symptomatic3": cp.Uniform(0.4, 0.6),
        # "CLP1": cp.Uniform(60, 400)
        #############
        # Leftovers #
        #############
        # "Kernel_scale": cp.Uniform(0.9*4000, 1.1*4000),
        # "Kernel_Shape": cp.Uniform(0.8*3, 1.2*3),
        # "Kernel_shape_params_for_place_types0": cp.Uniform(0.8*3, 1.2*3),
        # "Kernel_shape_params_for_place_types1": cp.Uniform(0.8*3, 1.2*3),
        # "Kernel_shape_params_for_place_types2": cp.Uniform(0.8*3, 1.2*3),
        # "Kernel_shape_params_for_place_types3": cp.Uniform(0.8*3, 1.2*3),
        # "Kernel_scale_params_for_place_types0": cp.Uniform(0.9*4000, 1.1*4000),
        # "Kernel_scale_params_for_place_types1": cp.Uniform(0.9*4000, 1.1*4000),
        # "Kernel_scale_params_for_place_types2": cp.Uniform(0.9*4000, 1.1*4000),
        # "Kernel_scale_params_for_place_types3": cp.Uniform(0.9*4000, 1.1*4000),
        # "Param_1_of_place_group_size_distribution0": cp.DiscreteUniform(20, 30),
        # "Param_1_of_place_group_size_distribution1": cp.DiscreteUniform(20, 30),
        # "Param_1_of_place_group_size_distribution2": cp.DiscreteUniform(80, 120),
        # "Param_1_of_place_group_size_distribution3": cp.DiscreteUniform(8, 12),
        # "Proportion_of_between_group_place_links0": cp.Uniform(0.8*0.25, 1.2*0.25),
        # "Proportion_of_between_group_place_links1": cp.Uniform(0.8*0.25, 1.2*0.25),
        # "Proportion_of_between_group_place_links2": cp.Uniform(0.8*0.25, 1.2*0.25),
        # "Proportion_of_between_group_place_links3": cp.Uniform(0.8*0.25, 1.2*0.25),
    }
    
    #=================================
    #create dimension-adaptive sampler
    #=================================
    #sparse = use a sparse grid (required)
    #growth = use a nested quadrature rule (not required)
    #midpoint_level1 = use a single collocation point in the 1st iteration (not required)
    #dimension_adaptive = use a dimension adaptive sampler (required)
    sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=1,
                                    quadrature_rule="C",
                                    sparse=True, growth=True,
                                    midpoint_level1=True,
                                    dimension_adaptive=True)
    
    campaign.set_sampler(sampler)
    
    print('Number of samples = %d' % sampler._number_of_samples)
    
    campaign.draw_samples()
    campaign.populate_runs_dir()
    
    # run the UQ ensemble
    fab.run_uq_ensemble(config, campaign.campaign_dir, script='CovidSim',
                        machine="eagle_vecma", PilotJob = False)
    #wait for job to complete
    fab.wait(machine="eagle_vecma")
    
    #wait for jobs to complete and check if all output files are retrieved 
    #from the remote machine
    fab.verify(config, campaign.campaign_dir, 
               campaign._active_app_decoder.target_filename, 
               machine="eagle_vecma", PilotJob=False)
    
    #run the UQ ensemble
    fab.get_uq_samples(config, campaign.campaign_dir, sampler._number_of_samples,
                       machine='eagle_vecma')
    campaign.collate()
    
    # Post-processing analysis
    analysis = uq.analysis.SCAnalysis(
        sampler=campaign._active_sampler,
        qoi_cols=output_columns
    )
    
    campaign.apply_analysis(analysis)
else:
    #reload Campaign, sampler, analysis
    campaign = uq.Campaign(state_file="covid_easyvvuq_state" + ID + ".json", 
                           work_dir=work_dir)
    print('========================================================')
    print('Reloaded campaign', campaign.campaign_dir.split('/')[-1])
    print('========================================================')
    sampler = campaign.get_active_sampler()
    sampler.load_state("covid_sampler_state" + ID + ".pickle")
    campaign.set_sampler(sampler)
    analysis = uq.analysis.SCAnalysis(sampler=sampler, qoi_cols=output_columns)
    analysis.load_state("covid_analysis_state" + ID + ".pickle")

max_iter = 100
max_samples = -3000
n_iter = 0

while n_iter <= max_iter and sampler._number_of_samples < max_samples:
    #required parameter in the case of a Fabsim run
    skip = sampler.count

    #look-ahead step (compute the code at admissible forward points)
    sampler.look_ahead(analysis.l_norm)

    #proceed as usual
    campaign.draw_samples()
    campaign.populate_runs_dir()

    #run the UQ ensemble at the admissible forward points
    #skip (int) = the number of previous samples: required to avoid recomputing
    #already computed samples from a previous iteration
    fab.run_uq_ensemble(config, campaign.campaign_dir, script='CovidSim',
                        machine="eagle_vecma", skip=skip, PilotJob=False)

    #wait for jobs to complete and check if all output files are retrieved 
    #from the remote machine
    fab.verify(config, campaign.campaign_dir, 
               campaign._active_app_decoder.target_filename, 
               machine="eagle_vecma", PilotJob=False)

    fab.get_uq_samples(config, campaign.campaign_dir, sampler._number_of_samples,
                       machine='eagle_vecma')

    campaign.collate()
    
    #compute the error at all admissible points, select direction with
    #highest error and add that direction to the grid 
    data_frame = campaign.get_collation_result()
    #catch IndexError, happens when not all samples are present the go to verify_ensemble, get_uq_samples, collate
    analysis.adapt_dimension(output_columns[0], data_frame, 
                             method=method)
    
    #save everything
    campaign.save_state("covid_easyvvuq_state" + ID + ".json")
    sampler.save_state("covid_sampler_state" + ID + ".pickle")
    analysis.save_state("covid_analysis_state" + ID + ".pickle")
    n_iter += 1

#merge accepted and admissble indices
# analysis.merge_accepted_and_admissible()

#apply analysis
campaign.apply_analysis(analysis)
results = campaign.get_last_analysis()

#################################
# Plot some convergence metrics #
#################################

analysis.adaptation_histogram()

params = list(sampler.vary.get_keys())
sobols = results['sobols_first'][output_columns[0]]
tmp = np.array([sobols[params[i]][-1] for i in range(analysis.N)]).flatten()
idx = np.flipud(np.argsort(tmp))
analysis.adaptation_table(order=idx)

analysis.plot_stat_convergence()
surplus_errors = analysis.get_adaptation_errors()
fig = plt.figure()
ax = fig.add_subplot(111, xlabel = 'refinement step', ylabel='max surplus error')
ax.plot(range(1, len(surplus_errors) + 1), surplus_errors, '-b*')
plt.tight_layout()

# #########################
# # plot mean +/- std dev #
# #########################

fig = plt.figure()
ax = fig.add_subplot(111, xlabel="days", ylabel=output_columns[0])
mean = results["statistical_moments"][output_columns[0]]["mean"]
std = results["statistical_moments"][output_columns[0]]["std"]
ax.plot(mean)
ax.plot(mean + std, '--r')
ax.plot(mean - std, '--r')
plt.tight_layout()

#############
# Load data #
#############

import pandas as pd
df = pd.read_csv('./data/data_2020-Jul-27.csv')
cumDeath_data = np.flipud(df['cumDeathsByPublishDate'].values)
dates_data = np.flipud(df['date'])
day_start = 65  #March 6 is first datapoint, is day 66 so index 65

########################
# Load report 9 result #
########################

df = pd.read_csv('./data/report9.csv', delimiter='\t')
cumDeath_rep9 = df['cumDeath'].values

# #################################
# # Plot the confidence intervals #
# #################################

# n_samples = 500

# #draw n_samples draws from the input distributions
# xi_mc = np.zeros([n_samples, analysis.N])
# idx = 0
# for dist in sampler.vary.get_values():
#     xi_mc[:, idx] = dist.sample(n_samples)
#     idx += 1

# #sample the surrogate n_samples times
# surr_samples = np.zeros([n_samples, analysis.N_qoi])
# print('Sampling surrogate %d times' % (n_samples,))
# for i in range(n_samples):
#     surr_samples[i, :] = analysis.surrogate(output_columns[0], xi_mc[i])
#     if np.mod(i, 10) == 0:
#         print('%d of %d' % (i + 1, n_samples))
# print('done')

from matplotlib import gridspec
import seaborn as sns

x = range(analysis.N_qoi)

surr_samples = analysis.get_sample_array(output_columns[0])
n_samples = surr_samples.shape[0]

#confidence bounds
lower1, upper1 = analysis.get_confidence_intervals(output_columns[0], n_samples, conf=0.63,
                                                    surr_samples=surr_samples)
lower2, upper2 = analysis.get_confidence_intervals(output_columns[0], n_samples, conf=0.95,
                                                    surr_samples=surr_samples)

fig = plt.figure(figsize=(10,5))
spec = gridspec.GridSpec(ncols=2, nrows=1,
                          width_ratios=[3, 1])

ax1 = fig.add_subplot(spec[0], xlim=[0, 840], ylim=[-100, 80000])
ax2 = fig.add_subplot(spec[1], sharey=ax1)
ax2.get_xaxis().set_ticks([])
fig.subplots_adjust(wspace=0)
plt.setp(ax2.get_yticklabels(), visible=False)

ax1.fill_between(x, lower2, upper2, color='#aa99cc', label='95% CI', alpha=0.5)
ax1.fill_between(x, lower1, upper1, color='#aa99cc', label='68% CI')

mean = results["statistical_moments"][output_columns[0]]["mean"]
ax1.plot(x, mean, label='Mean')

#plot a single sample of report 9
ax1.plot(cumDeath_rep9, '--', color='#ffb20a', label=r'Baseline report 9 sample', linewidth=3)

#plot data
ax1.plot(np.arange(day_start, day_start + cumDeath_data.size)[0:-1:7],
         cumDeath_data[0:-1:7], 's', color='olivedrab', label='Data')

ax1.legend(loc="upper left")

ax1.set_xlabel('Days')
ax1.set_ylabel('Cumulative deaths')
# ax2.set_xlabel('Frequency')
#ax2.set_title('Total deaths distribution')
ax2.axis('off')

total_deaths = surr_samples[:, -1]
ax2 = sns.distplot(total_deaths, vertical=True)

plt.tight_layout()
##################################
# Plot first-order Sobol indices #
##################################

from itertools import cycle

# color = cycle(['b', 'r', 'g', 'm', 'c', 'k'])
marker = cycle(['o', 'v', '^', '<', '>', 's', '*', 'p', 'd', 'P', 'X'])
skip = 30
x = range(0, analysis.N_qoi, skip)

fig = plt.figure(figsize=[10, 5])
ax = fig.add_subplot(121, title=r'First-order Sobols indices',
                      xlabel="days", ylabel=r'$S_i$', ylim=[0,1])
sobols_first = results["sobols_first"][output_columns[0]]

first_order_contribution = 0

highlight = ['Relative_spatial_contact_rate_given_social_distancing',
             'Relative_place_contact_rate_given_social_distancing_by_place_type3',
             'Delay_from_end_of_latent_period_to_start_of_symptoms',
             'Latent_period']
highlight_contribution = 0

for param in sobols_first.keys():
    ax.plot(x, sobols_first[param][0:-1:skip], label=param, marker=next(marker))
    first_order_contribution += sobols_first[param][0:-1:skip]
    if param in highlight:
        highlight_contribution += sobols_first[param][0:-1:skip]
    
ax.plot(x, first_order_contribution, 'b*', label=r'First-order contribution')
ax.plot(x, highlight_contribution, 'rd', label=r'Contribution 4 most important parameters')

leg = ax.legend(loc=0, fontsize=8)
leg.set_draggable(True)
plt.tight_layout()


#####################
# Robustness factor #
#####################

analysis.get_uncertainty_blowup(output_columns[0])

# qoi = 'cumDeath'
# conf = 0.9
# alpha = (1.0 - conf)/2

# samples = analysis.get_sample_array(qoi)
# samples = np.sort(samples, axis=0)
# S = samples.shape[0]

# L = int(alpha*S)
# U = int((1-alpha)*S)

# lower = samples[L, :]
# upper = samples[U, :]

# N_bootstrap = 10000

# delta_lower = np.zeros([N_bootstrap, samples.shape[1]])
# delta_upper = np.zeros([N_bootstrap, samples.shape[1]])

# for i in range(N_bootstrap):
#     idx = np.random.randint(0, S-1, S)
#     resample = np.sort(samples[idx], axis=0)
    
#     delta_lower[i] = resample[L, :] - lower
#     delta_upper[i] = resample[U, :] - upper

# delta_lower = np.sort(delta_lower, axis=0)
# delta_upper = np.sort(delta_upper, axis=0)

# plt.plot((lower - delta_lower).T, 'r', alpha=0.1)
# plt.plot((upper - delta_upper).T, 'r', alpha=0.1)
# plt.plot(lower, 'b')
# plt.plot(upper, 'b')    

plt.show()