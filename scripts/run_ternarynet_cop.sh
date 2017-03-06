#!/bin/bash

sqsub -q gpu -f mpi -n 8 -r 7d -o /scratch/$USER/%J.out --gpp=4 --mpp=92g --nompirun ./scripts/run_ternarynet.sh
