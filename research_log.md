06/02/2026

Created the repo where all of the data for the project will be stored along with all of the python scripts needed for data exctraction and conversion.

Set up OrbFit in my linux environment.

15/02/2026

A python script to extract the telescope data from the LCO FITS files so that Astrometrica can compute the reduction properly needs to be written.

27/02/2026

The script to extract all of the Astrometrica settings has been written. There are a couple issues that I need fix along with verifying and adding all of the MPC codes.

As this script contains the MPC codes the origional script with just the MPC code extraction is now redundant, but it will stay in the repo to show the development of my project.
 
10/03/2026

The OrbFit source code was compiled successfully using gfortran 13.3.0, producing the key executables orbfit.x, fitobs.x, orbit9.x, and bineph.x with no fatal errors. The JPL DE405 planetary ephemeris (covering years 1600–2200) was downloaded from the NASA JPL FTP server, noting that the reference solutions were built with DE431 alongside the pre-computed AST17 asteroid perturbations, but differences are negligible. A six-parameter orbit determination test was run for 1862 Apollo using fitobs.x with the fcct14 error model, converging to a weighted RMS residual of 0.579 arc-seconds across 1,408 observations. This test did not include the Yarkovsky effect, which will be incorporated in subsequent work. A minor issue with a missing epoch/ directory was resolved manually, and the final orbital solution agreed with the DE431 reference to 6–10 significant figures across all elements, confirming the installation is working correctly. All input files, output solutions, and terminal logs were saved to the project GitHub repository under results/fitobs_validation_6dim/.

11/03/2026

The orbit9.x numerical integrator was validated by running the built-in test case, which integrated 2 main-belt asteroids and 4 giant planets backwards over 20,000 years using a 12th-order multistep method with automatic stepsize control. For the simulations I will run using my own data I will change dt from -200 to 200 or a larger step and increase n_out to simulate over the Myr scales I want to look at. The integration completed successfully and the output agreed with the DE431 reference solution to 7–8 significant figures, with small differences attributable to the use of DE405 for the barycentric initial conditions. All input files and output data were saved to the project GitHub repository under results/orbit9_validation_20kyr/.

01/06/2026 - Final Dissertation Update

The repository has been finalised in preparation for dissertation submission. All core scripts used in the computational pipeline have now been uploaded and the research log has been updated to reflect the completed development and validation work. This version represents the final state of the project as submitted for assessment.
