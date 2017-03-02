#!/bin/bash

module unload intel mkl openmpi 
module load intel/15.0.3 
module load openmpi/intel1503-std/1.8.7
module load hdf/serial/5.1.8.11 
module load python/intel/2.7.10
export LD_LIBRARY_PATH=/opt/sharcnet/testing/cudnn/cudnn4:$LD_LIBRARY_PATH
export PYTHONPATH=$PYTHONPATH:/opt/sharcnet/opencv/2.4.9/lib/python2.6/site-packages/:/home/laceyg/Personal/ternarynet
export TENSORPACK_DATASET=/tmp/MLRG/ilsvrc12/
