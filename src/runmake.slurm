#!/bin/bash
#SBATCH -J Makewisdom
#SBATCH -p cpu-quota
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -o makeSTD.log
#SBATCH -e makeERR.log

make makewisdom
