



# FabCovidsim
This is a FabSim3 / EasyVVUQ plugin for Covid-19 simulation. It was used to compute the ensembles of the following paper:

Edeling, Wouter and Hamid, Arabnejad and Sinclair, Robert and Suleimenova, Diana and Gopalakrishnan, Krishnakumar and Bosak, Bartosz and Groen, Derek and Mahmood, Imran and Crommelin, Daan and Coveney, Peter, *The Impact of Uncertainty on Predictions of the CovidSim Epidemiological Code*, 2020.

In the first section we will detail the FabSim3 commands used for ensemble execution. The the section following that we discuss the EasyVVUQ script for dimension-adaptive sampling, and show how these commands are integrated in Python.

## Dependencies:

[FabSim3](https://github.com/djgroen/FabSim3.git) : `git clone https://github.com/djgroen/FabSim3.git`

[COVID-19 CovidSim microsimulation model developed Imperial College, London](https://github.com/mrc-ide/covid-sim)


## Installation
Simply type `fab localhost install_plugin:FabCovidsim` anywhere inside your FabSim3 install directory.

### FabSim3 Configuration
Once you have installed the required dependencies, you will need to take a few small configuration steps:
1. Go to `(FabSim Home)/deploy`
2. Open `machines_user.yml`
3. for `qcg` machine, add these lines
``` yaml
qcg:
  ...
  ...
  # setting for Imperial College COVID-19 simulator
  cores: 28
  budget: "vecma2020"
  # job wall time for each job, format P[nD]T[nH][nM]
  # nD - number of days, nH - number of hours, nM - number of minutes
  job_wall_time : "PT20M" # job wall time for each single job without PJ
  PJ_size : "2" # number of requested nodes for PJ
  PJ_wall_time : "PT50M" # job wall time for PJ
  modules:
    loaded: ["python/3.7.3", "r/3.6.1-gcc620"] # do not change
    unloaded: [] #
```
4. for `eagle_vecma` machine, add these lines
``` yaml
eagle_vecma:
  ...
  ...
  # setting for Imperial College COVID-19 simulator
  cores: 28
  budget: "vecma2020"
  # job wall time for each job, format Days-Hours:Minutes:Seconds
  job_wall_time : "0-0:20:00" # job wall time for each single job without PJ
  PJ_size : "2" # number of requested nodes for PJ
  PJ_wall_time : "0-00:50:00" # job wall time for PJ
  modules:
    loaded: ["python/3.7.3", "r/3.6.1-gcc620"] # do not change
    unloaded: [] #
```    
   <br/> _NOTE: you can changes the values of these attributes, but do not change the modules load list._
  
## Job submission via command line
1. To run a single job, simply type:
  >``` sh
  > fab <qcg/eagle_vecma> CovidSim:UK_sample[,memory=MemorySize][,label=your_lable]
  > ```   
  > _NOTE:_
  >   - by default **memory=20GB** .
  >   

2. To run the ensemble, you can type, simply type:
  >``` sh
  > fab <qcg/eagle_vecma> CovidSim_ensemble:UK_sample[,<memory=MemorySize>][,replicas=replica_number]
  > ```   
  > _NOTE:_
  >   -  **replicas=N** : will generate N replicas
  >    - if you want to run multiple simulations with different configuration, to do that, create your own folder name under `SWEEP` directory, and change the parameters files, there are some examples under `/config_files/SWEEP_examples` folder,
  >    - if you want to use QCG-PJ with `eagle_vecma` make sure that you first install it by `fab eagle_vecma install_app:QCG-PilotJob,virtual_env=True`
  >
  > _Examples:_
  >   -  `fab eagle_vecma CovidSim_ensemble:UK_sample`
  >   -  `fab qcg CovidSim_ensemble:UK_sample,PilotJob=True`
  >   -  `fab qcg CovidSim_ensemble:UK_sample,replicas=5,PilotJob=True`
  >   -  `fab eagle_vecma CovidSim_ensemble:UK_sample,PilotJob=True`
  >   -  `fab eagle_vecma CovidSim_ensemble:UK_sample,replicas=5`

## Running a standard EasyVVUQ - CovidSim campaign via Python

NOTE: As is stands now, everything below needs EasyVVUQ functionality present in the `dev` branch, so check out this branch first.

This demonstrates how to use a standard EasyVVUQ campaign on the CovidSim code. By 'standard' we mean non-dimension adaptive, where each input parameter is sampled equally. There are two Python scripts that need to be executed:

1. `standard_covid_easyvvuq/covid_init_SC.py`: a standard EasyVVUQ campaign up to and including job submission.
2. `standard_covid_easyvvuq/covid_analyse_SC.py`: job retrieval and post processing.

The `FabCovidSim` plugin is called from within `standard_covid_easyvvuq/covid_init_SC.py` via
``` python
import fabsim3_cmd_api as fab
fab.run_uq_ensemble(config, campaign.campaign_dir, script="CovidSim",
                    machine="eagle_vecma", PilotJob=True)
```
Here, `config` is the name of the config file directory that is used for the code, which are located in `config_files/`. Furthermore `script="CovidSim"` refers to `/templates/CovidSim`, which contains the instructions to execute a single job.

To retrieve the results from the remote machine, the following is executed in `standard_covid_easyvvuq/covid_analyse_SC.py`:
``` python
fab.get_uq_samples(config, campaign.campaign_dir, sampler._number_of_samples,
                   machine='eagle_vecma')
```

## Running a dimension-adaptive EasyVVUQ - CovidSim campaign via Python

The file `final_adaptive_covid_easyvvuq/covid_automated.py` contains the dimension-adaptive EasyVVUQ script that we used to produce the results of the article above. Running this file will require you to checkout the `CovidSim` branch of EasyVVUQ. We will go through the script step by step, which starts with the initial iteration of the dimension-adaptive sampler.

### Initial iteration ###

```python
output_columns = ["cumDeath"]
work_dir = '/home/wouter/VECMA/Campaigns'
config = 'PC_CI_HQ_SD_suppress_campaign_full1_19param_4'
ID = '_recap2_surplus'
method = 'surplus'
```

Here `output_columns` is a list containing the name of the column in the CovidSim output csv file that we use as our Quantity of Interest (QoI). Here we used the cumulative deaths. In a dimension-adaptive setting this list should contain only one QoI. The `work_dir` is where the EasyVVUQ Campaign will be stored, and `config` must match a directory name in the `config_files` directory of FabCovidSim. These config directories contain all the files needed to run CovidSim with at a specified setting. In particular, examine the `run_sample.py` file in these config directories. This file is responsible for passing the commandline parameters (seeds, R0 and ICU triggers) to CovidSim. We specify the seeds from within EasyVVUQ, and the other two are hard coded.

Above, `ID` is just a unique identifier that we use to save the state of EasyVVUQ, and `method` is the error method that we use in the dimension adaptive sampling. Here, the sampling plan is refined by using the hierarchical surplus.

Next we have

```python
    params = json.load(open(home + '/../templates_campaign_full1/params.json'))
```
This loads a JSON file with all CovidSim parameters, and their default values. This file was created during the making of the EasyVVUQ input file templates. These templates are made using the scripts in the `make_template` folder of FabCovidSim. CovidSim has two main input files, for instance `p_PC_CI_HQ_SD.txt` and `preGB_R0=2.0.txt`. The template scripts take a standard CovidSim input file and replaces the default values with a flag that EasyVVUQ can seed with values drawn from a specified input distribution. This is done by the Encoder elements of EasyVVUQ:
```python
    # Create an encoder
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
```
 This code tells EasyVVUQ that CovidSim expects a `param_files` directory with three input files in it (`p_PC_CI_HQ_SD.txt`, `preGB_R0=2.0.txt` and `p_seeds.txt`). Here we used the standard [Jinja](https://jinja.palletsprojects.com/en/2.11.x/) Encoder, and a custom encoder (`final_adaptive_covid_easyvvuq/custom.py`). We used the latter because we parameterized one of the vector-valued inputs of CovidSim, see the paper for details. Next we have the EasyVVUQ decoder element:
 
 ```python
     decoder = uq.decoders.SimpleCSV(
        target_filename='output_dir/United_Kingdom_PC_CI_HQ_SD_R0=2.6.avNE.severity.xls', 
        output_columns=output_columns, header=0, delimiter='\t')
 ```
This tells EasyVVUQ the name and the format of CovidSim's output files, of which `cumDeath` is one of the columns. We store all the predictions in an single HDF5 data file for analysis via

```python
    collater = uq.collate.AggregateHDF5()
```

To put all UQ elements together we execute

```python
    # Add the app
    campaign.add_app(name=config,
                     params=params,
                     encoder=multiencoder_p_PC_CI_HQ_SD,
                     collater=collater,
                     decoder=decoder)
    # Set the active app 
    campaign.set_app(config)
```

The `vary` dict contains all input parameters we wish to vary, where we use [Chaospy](https://chaospy.readthedocs.io/en/master/) to specify the input distributions

```python
    vary = {
        ###########################
        # Intervention parameters #
        ###########################
        "Relative_household_contact_rate_after_closure": cp.Uniform(1.5*0.8, 1.5*1.2),
        ...
```

We select the dimension-adaptive Stochastic Collocation sampler via:
```python
sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=1,
                                quadrature_rule="C",
                                sparse=True, growth=True,
                                midpoint_level1=True,
                                dimension_adaptive=True)
campaign.set_sampler(sampler)
```
Here:

* `polynomial_order=1`: do not change, will be adaptively increased for influential parameters. (Technically, it'll change the quadrature order for different (combinations of) parameters)
* `quadrature_rule="C":`selects the Clenshaw Curtis quadrature rule. This not required, although it is common.
* `sparse = True`: selects a sparse grid. This is required.
* `growth = True`: selects a nested quadrature rule (a quadrature rule such that a 1D rule of order p contains all points of the same rule of order p-1). Also not required, but is efficient in high dimensions. Note that this can only be selected with a subset of all quadrature rules in Chaospy, including Clenshaw Curtis.
* `midpoint_level1=True`: this means that the first iteration of the dimension-adaptive sampler consists of a single sample. 
* `dimension_adaptive=True`: selects the dimension-adaptive sparse grid sampler (opposed to the isotropic sparse grid sampler, which treats each input the same).

We draw the input samples and create the run directories in `work_dir` via:

```python
campaign.draw_samples()
campaign.populate_runs_dir()
```

Next is it time to execute the first ensemble (which will just consist of a single sample):

```python
    # run the UQ ensemble
    fab.run_uq_ensemble(config, campaign.campaign_dir, script='CovidSim',
                        machine="eagle_vecma", PilotJob = False)
    
    #wait for jobs to complete and check if all output files are retrieved 
    #from the remote machine
    fab.verify(config, campaign.campaign_dir, 
                campaign._active_app_decoder.target_filename, 
                machine="eagle_vecma", PilotJob=False)
    
    #run the UQ ensemble
    fab.get_uq_samples(config, campaign.campaign_dir, sampler._number_of_samples,
                       skip=0, max_run=1, machine='eagle_vecma')

```

The comments above each command are self explanatory. Basically `fab` is an interface between Python and the FabSim3 commands found above (e.g. `CovidSim_ensemble`), that we use to execute the ensemble. Here we run the ensembles on the PSNC Eagle supercomputer in Poland. The basic steps are: 1) send ensemble to Eagle, 2) wait for jobs to complete, 3) copy results back to the FabSim results directory on the localhost and check if all output files are present, and 4) copy the results to `work_dir`.

To run the samples on Eagle, we used 28 cores (1 node) per sample. This is specified in FabSim's `machine_user.yml` file, see the FabSim3 configuration section above. We then collate the results in the HDF5 dataframe and create a Stochastic Collocation analysis object:

```python
    campaign.collate()
    
    # Post-processing analysis
    analysis = uq.analysis.SCAnalysis(
        sampler=campaign._active_sampler,
        qoi_cols=output_columns
    )
    
    campaign.apply_analysis(analysis)
```

This concludes the initial iteration.

### Refining the sampling plan ###

We now have computed a single sample of CovidSim, which we will start to refine in an iterative fashion. The loop we use for this purpose is given by

```python
max_iter = 5000
max_samples = 3000
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
                       skip=skip, max_run=sampler.count, machine='eagle_vecma')

    campaign.collate()

    #compute the error at all admissible points, select direction with
    #highest error and add that direction to the grid 
    data_frame = campaign.get_collation_result()
    #catch IndexError, happens when not all samples are present the go to verify_ensemble, get_uq_samples, collate
    analysis.adapt_dimension(output_columns[0], data_frame, 
                             method=method)

    #save everything
    campaign.save_state("states/covid_easyvvuq_state" + ID + ".json")
    sampler.save_state("states/covid_sampler_state" + ID + ".pickle")
    analysis.save_state("states/covid_analysis_state" + ID + ".pickle")
    n_iter += 1
```

Many commands are similar to those we have seen before. The main difference is the appearance of `look_ahead` and `adapt_dimension`.

*Look_ahead*

We start with `sampler.look_ahead(analysis.l_norm)`. First, `l_norm` is a set of multi indices, denoting the order of the 1D quadrature (and therefore the number of points) used per input parameter. For instance:
``` python
l_norm = array([[1, 1]])
```
means we have 2 input parameters, both of which have a 1D quadrature rule of order 0. Lets say the chosen quadrature rule generates `x = [0.5]` as point for order 0. Then the 2D grid is built as a tensor product `[0.5] x [0.5] = [0.5, 0.5]`. Hence `l_norm = array([[1, 1]])` means we have a 2D grid consisting of just one point `[0,5, 0.5]`. If on the other hand we have
``` python
l_norm = array([[1, 1],
                [1, 2],
                [2, 1]])
```
we are building a grid using a linear combination of 3 tensor products. If our 1D quadrature rule generates `x = [0.0, 0.5, 1.0]` for order 1, our grid consistis of the points:
```python 
l_norm = [1, 1]  ==> [0.5] x [0.5] = [[0.5, 0.5]]
```
and
```python
l_norm = [1, 2]  ==> [0.5] x [0.0, 0.5, 1.0] = [[0.5, 0.0], [0.5, 0.5], [0.5, 1.0]]
```
and
```python
l_norm = [2, 1]  ==> [0.0, 0.5, 1.0] x [0.5] = [[0.0, 0.5], [0.5, 0.5], [1.0, 0.5]]
```
Notice that this makes a "cross" of 5 (unique) points in the input space. A standard EasyVVUQ campaign always has a single `l_norm`, such as for instance `[2,2]`, which leads to a full "square" of 9 points: `[0.0, 0.5, 1.0] x [0.0, 0.5, 1.0]`. Sparse grids on the other hand, build the grid from the bottom up, using a linear combination of `l_norm` multi indices, which can lead to more sparse sampling plans. 

The array `analysis.l_norm` contains the currently accepted multi indices, and therefore the current configuration of points. What `analysis.look_ahead(analysis.l_norm)` does is take these multi indices, and compute new "candidate" `l_norm` entries, which are stored in `sampler.admissible_idx`. These new candidate multi indices will (probably) contain unsampled points, which are then sampled using `fab.run_uq_ensemble` as before. The `skip` parameter is used to prevent recomputing already computed samples. We set it equal to the number of samples which are already computed through `skip=sampler.count`. 

*Adapt_dimension*

The function `analysis.adapt_dimension` takes the name of the quantity of interest (QoI), and the sample database as input. For every multi index in `sampler.admissible_idx`, it computes the so-called "hierarchical surplus error", which is the difference between the new sample of our QoI (`output_columns[0]`), and the polynomial approximation of that sample at the previous iteration. The surplus is therefore used as a local error estimator, and the multi index in `sampler.admissible_idx` with the highest surplus will get added to `analysis.l_norm`, and then `dummy_look_ahead.py` can get executed again. This goes round and round until we have spent our computational budget (3000 CovidSim samples in this case).

What follows in our Python script are just several post-processing steps to produces the Figures we used in the article.
