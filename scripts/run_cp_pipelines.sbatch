#!/bin/bash

#SBATCH --partition=roma
#SBATCH --nodes=1
#SBATCH --cpus-per-task=64
##SBATCH --exclusive
#SBATCH --time=20:00:00
#SBATCH --exclude=sdfrome034

cd ${PWD}
source ./setup.sh
run_cp_pipelines.py
