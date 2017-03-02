#!/bin/bash

sqsub -q gpu -f mpi -n 8 --gpp 4 -r 3600 -o %J.out --mpp=92g --nompirun screen -D -fn -m bash
