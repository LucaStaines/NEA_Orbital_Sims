# The use of orbital parameters to study the evolution of newly discovered asteroids.

## Project Overview

This repository contains the computational work for my MPhys project investigating 
the long-term orbital evolution of newly discovered Near-Earth Asteroids (NEAs). 
The project involves three main stages:

1. **Astrometric Reduction:** Processing images of newly discovered asteroids 
   obtained through the Las Cumbres Observatory (LCO) global telescope network 
   using Astrometrica to derive precise positional measurements.

2. **Orbit Determination:** Using the OrbFit software package to determine 
   orbital elements from the astrometric observations via differential corrections.

3. **Orbital Evolution Simulation:** Performing long-term numerical integrations 
   (Myr timescales) using OrbFit's orbit9 symplectic integrator to study the 
   dynamical evolution of the target asteroid(s), including planetary perturbations 
   and non-gravitational effects (Yarkovsky effect).

## Computational Environment

- OS: Ubuntu 24.04 LTS
- Compiler: GNU Fortran (gfortran) 13.3.0
- Planetary Ephemeris: JPL DE405 (1600–2200)
- Asteroid Perturbations: AST17 (16 major asteroids + Pluto)

## References
- M. Fenucci and B. Novaković: 2022. *Mercury and OrbFit packages for numerical integration of planetary systems: implementation of the Yarkovsky and YORP effects*, Serbian Astronomical Journal 204, pp. 51-63

## Versioning
This repository represents the state of the codebase at the time of MPhys dissertation submission (01/06/2026). Subsequent work is not part of the assessed submission and is recorded in the `future_work` file.

## Author

Luca Staines<br>
MPhys (Expected 2026)<br>
Swansea University<br>
Luca.staines@icloud.com
