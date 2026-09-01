# mu4-ip-verification
Integer programming verification that no covering family of [4]^4 of size 11 exists.

This repository contains the computation used to verify that no covering family of
[4]^4 of size 11 exists.

The problem is formulated as a binary integer feasibility problem. After normalizing
each first permutation to the identity, there are 13,824 candidate
blocks. A binary variable is introduced for each block. The constraints require that

- every element of [4]^4 is covered by at least one selected block;
- at most 11 blocks are selected.

The resulting model has 13,824 binary variables and 257 constraints.

HiGHS certifies that the model is infeasible. Therefore there is no covering family
of [4]^4 of size at most 11.

An explicit covering family of size 12 is given in the accompanying paper, so
kappa(4)=12, and hence mu(4)=12.

## Requirements

Python 3

Install the required packages with

    python -m pip install pulp highspy

## Run

    python verify_mu4_ip.py 4 11 highs

A successful verification ends with output of the form

    Solver status: Infeasible
    INFEASIBLE: no covering family of size <= 11.

## Sanity checks

The same program gives the expected results on the following instances:

    python verify_mu4_ip.py 3 5 highs    # infeasible
    python verify_mu4_ip.py 3 6 highs    # feasible
    python verify_mu4_ip.py 4 12 highs   # feasible

The first two agree with the known value kappa(3)=6, while the third agrees
with the explicit covering family of size 12 given in the paper.

## Computational environment

The computation reported in the paper was performed using Python 3.12,
PuLP 3.3.0, and HiGHS 1.15.1 on Windows 11.

## Runtime

The l=4, N=11 computation required approximately 99 minutes on the machine
used for the reported run. Runtime may vary with hardware and solver version.
