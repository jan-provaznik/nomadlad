#!/usr/bin/bash

mpirun -np 16 --oversubscribe \
  -- python3 -m mpi4py.futures wrapped.py

