"""
==============================================================================
THE LOOK-AHEAD STEP

Takes the current configuration of points, computes so-called adimissble
points in the look_forward subroutine. These points are used in 
the adaptation step to decide along which dimension to place more samples.

The look-ahead step and the adaptation step can be executed multiple times:
look ahead, adapt, look ahead, adapt, etc
==============================================================================
"""

import easyvvuq as uq
import os
# import tkinter as tk
# from tkinter import filedialog
import fabsim3_cmd_api as fab

home = os.path.abspath(os.path.dirname(__file__))
output_columns = ["cumDeath"]
work_dir = '/tmp'
config = 'dummy_covid'

# #load a Campaign state
# root = tk.Tk()
# root.withdraw()
# state_file = tk.filedialog.askopenfilename(title="Load Campaign state", 
#                                filetypes=(('json files', '*.json'), 
#                                           ('All files', '*.*')))
# ID = state_file.split('.json')[0][-1]
state_file = 'states/covid_easyvvuq_state.json'
campaign = uq.Campaign(state_file=state_file, work_dir=work_dir)
print('========================================================')
print('Reloaded campaign', campaign.campaign_dir.split('/')[-1])
print('========================================================')
sampler = campaign.get_active_sampler()
sampler.load_state("states/covid_sampler_state.pickle")
campaign.set_sampler(sampler)
analysis = uq.analysis.SCAnalysis(sampler=sampler, qoi_cols=output_columns)
analysis.load_state("states/covid_analysis_state.pickle")

#required parameter in the case of a Fabsim run
skip = sampler.count

#look-ahead step (compute the code at admissible forward points)
sampler.look_ahead(analysis.l_norm)

#proceed as usual
campaign.draw_samples()
campaign.populate_runs_dir()

#save campaign and sampler
campaign.save_state("states/covid_easyvvuq_state.json")
sampler.save_state("states/covid_sampler_state.pickle")

#run the UQ ensemble at the admissible forward points
#skip (int) = the number of previous samples: required to avoid recomputing
#already computed samples from a previous iteration
fab.run_uq_ensemble(config, campaign.campaign_dir, script='Dummy_CovidSim',
                    machine="localhost", skip=skip)