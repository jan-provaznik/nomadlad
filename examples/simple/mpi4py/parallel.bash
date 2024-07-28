#!/usr/bin/bash

mpirun -np 16 --oversubscribe -x PATH \
  -- python3 -m mpi4py.futures parallel.py

