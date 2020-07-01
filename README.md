# Overview
This is a subset of the project `Genetic Circuit Design` for Boston University 
Class EC/BE522 - Computational Synthetic Biology for Engineers.

This repository is for the technical interview portion for the position of 
Software Engineer at the DAMP Lab at Boston University. In this readme I will 
detail my technical choices and design decision to demonstrate my proficiency in
software engineering.

# How to run
Assuming familiarity with the conda ecosystem:
- `git clone https://github.com/0x174/pegbox.git`
- `cd pegbox`
- `conda env create -f environment.yml`
- `conda activate pegbox-dev`
- `pytest`

Due to some technical difficulties with interacting with the remote endpoint, 
I've encapsulated most of the functionality in terms of optimization into
testing files that show the general pattern for generating circuits and 
optimizing them. 

I have also written out a new python3.6+ API for interacting 
with the Cello service, but it is untested due to the above factors.

# Design Choices
## Algorithm Selection 
Scipy offers a variety of minimization algorithms, each of which has strengths 
and weaknesses. I hedged my bets by creating a uniform interface that allowed the user to select which 
algorithm would best be suited to their problem.

## Tooling Choice
My choice of using Python was primarily motivated by the scientific library ecosystem 
and development speed.

If I were to have more time and this was deployed less as a script and
more as a remote service as some form of optimization for Cello input in the 
wild, I would move to a more statically typed language for execution speed, either
through some compiled cython bindings, subprocess calls to compiled C/C++, or 
something more exotic like Julia if I'm really trying to wring performance out and
I can trust that the interface is going to be fairly stable.

## Challenges
My challenge related to this project were ultimately related to understanding
the problem, which really took two major forms:

1) Understanding the semi-analog state of repressors and how they interact together.

2) Learning about the benefits and drawbacks of optimization algorithms and 
    correct selection thereof.
