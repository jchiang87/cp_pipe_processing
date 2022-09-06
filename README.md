# cp_pipe_processing

## Running at s3df
Contents of a possible setup script:
```
# Use the cvmfs distributions of lsst_distrib.
weekly_version=w_2022_36  # Set this as desired.
source /cvmfs/sw.lsst.eu/linux-x86_64/lsst_distrib/${weekly_version}/loadLSST-ext.bash
setup lsst_distrib

# Set up the gen3_workflow package for running bps.
IandT_SW=/fs/ddn/sdf/group/lsst/software/IandT/bps_env
setup -r ${IandT_SW}/gen3_workflow -j
export BPS_WMS_SERVICE_CLASS=desc.gen3_workflow.ParslService

# The following is needed to have access to the parsl and work_queue modules:
wq_env=${IandT_SW}/wq
export PYTHONPATH=${wq_env}/lib/python3.10/site-packages:${PYTHONPATH}
export PATH=${wq_env}/bin:${PATH}

export OMP_NUM_THREADS=1
export NUMEXPR_MAX_THREADS=1

# Set up this package:
setup -r <path_to>/cp_pipe_processing -j

# Set the data repo to use:
export BUTLER_CONFIG=/sdf/group/rubin/repo/main
```

### Running a pipeline
One can either use `srun` or `sbatch` to allocate resources on a shared node, in which case, the desired number of cpus per task should be set.  Alternatively, one can request a node exclusively with the `--exclusive` option (and omitting `--cpus-per-task`).
Here we ask for 32 cpus (with 4G of memory per cpu, by default) on a shared node:
```
$ srun --pty --cpus-per-task=32 bash
```
The default time limit for an allocation is currently 10 hours.  Once the allocation is granted, source the above example setup script to set up the Rubin code, etc..

Running a pipeline under `bps` is then as simple as
```
$ bps submit <path_to>/bps_cpBias.yaml
```
