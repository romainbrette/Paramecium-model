These are scripts to fit models to _Paramecium_ recordings, and produce figures for the following paper:
An electrophysiological and kinematic model of Paramecium, the “swimming neuron”
Irene Elices, Anirudh Kulkarni, Nicolas Escoubet, Léa-Laetitia Pontani, Alexis Prevost, Romain Brette

Contact : romain.brette@inserm.fr

Requirements:
* Model fitting toolbox of Brian 2 (https://github.com/brian-team/brian2modelfitting)
* Clampy (https://github.com/romainbrette/clampy): to read data files.
* For the behavioral model: PyQuaternion, quaternion, Scikit-image, and imageio with imageio-ffmpeg (to generate mp4s).
* OpenPIV for PIV analysis.
* PyYAML

Scripts that run in parallel (e.g. on a cluster) require GNU parallel.

### General organization

* `behavior/`: behaving models.
    * `models.py`: equations and parameter values for fitted models.
    * `motion.py`: simulation of Paramecium kinematics.
    * `motion_vectorized.py`: vectorized simulation of Paramecium kinematics (for many cells).
* `experiments/`: experimental scripts.
    * `current_pulses_analysis.py` : plots some basic analyses of the data.
    * `current_pulses_experiment.py` : performs a current pulse experiment. By default, runs on a RC model.
    * `lucam.py` : driver module for Lucam cameras.
    * `lucamcamera.py` : module to control a Lucam camera.
    * `notes.yaml` : a notes file to fill in before the experiment.
    * `setup_camera.py` : setup script for the Lucam camera.
    * `utils.py` : a few utilities file for runnings experiments.
* `file_management/`: tools for managing files.
    * `.paramecium_model_fitting.yaml`: an example configuration file, to edit and put in the home folder.
    * `batch_processing.py`: functions to run scripts and functions in parallel on multiple cell and
protocol folders.
    * `configuration.py`: getting information from the configuration file.
    * `data_preparation.py`: functions to select and process data.
    * `file_utils.py`: functions to deal with files and directories.
    * `folder_information.py`: functions to extract information from protocol
    folders.
    * `load_data.py`: data loading.
    * `load_models.py`: functions to load model descriptions.
    * `units_conversion.py`: functions to read and write numbers with units.
* `fitting/`: fitting and running models.
    * `fitting.py`: functions for fitting models to data and associated utilities.
    * `piv.py`: functions to deal with processed PIV data.
    * `run_model.py`: running an optimized model on data.
* `gui/`: GUI tools.
    * `image_gui.py`: a parameterized GUI for image annotation.
* `hydrodynamics/`: hydrodynamics calculations.
    * `sphere.py`: calculation of motion parameters from local forces on a sphere.
* `models/`: model descriptions.
    * `components/`: models of currents and other processes (calcium dynamics, electromotor coupling).
    * `full_models/`: complete models, and a table of constants for all fitted ciliated cells.
* `plotting`: plotting tools.
    * `draw_cell.py`: plots Paramecium cells.
    * `plots.py`: functions to plot traces.
* `scripts/`: scripts to fit models and analyze data.
    * `analysis/`: analysis of fitting results.
        * `compare_deciliated_fits.py`: performance comparison of different models fitted to deciliated cells.
        * `compare_hyperpolarized_fits.py`: performance comparison of different models fitted to hyperpolarized
        responses of ciliated cells.
        * `display_all_fits.py`: shows fits and real traces for all fitted cells, for a given fit.
        * `noise_analysis.py:`: analysis of noise in ciliated cells`.
        * `sedimentation/.py`: analyzes particle density vs. time in PIV movies.
        * `selection_ciliated.py`: selects ciliated fits with plausible parameters.
        * `selection_deciliated.py`: selects deciliated fits with plausible parameters.
        * `selection_hyperpolarized.py`: selects hyperpolarized fits with plausible parameters.
    * `bash/`: bash scripts to run model fitting on a cluster and copy the results.
        * `fit.sh`: runs multiple model fitting scripts on a directory.
        * `fit_and_archive.sh`: runs a fitting script and archive the results.
        * `make_archive.sh`: creates an archive of fitting results.
        * `sync_results.sh`: downloads through FTP and uncompresses fitting results.
    * `data_preparation/`: processing of data.
        * `extract_info.py`: extract information from cell folders.
        * `make_movie.py`: makes mp4 movies from tiff files.
        * `make_tables.py`: makes tables of fitted parameters for all cells, one table per fit.
        * `movie_to_tiff.py`: splits an mp4 movie into tiff files.
        * `morphology.py`: a GUI to annotate cell images for morphological measurements.
    * `figures/`: figures of the paper.
    * `fitting/`: fitting scripts. For all scripts, the calling argument is the cell folder on which to
    run the fit, or a folder containing multiple cell folders, in which case the script is run in parallel.
    * `image_analysis/`: analysis of camera data.
        * `fix_positions`: swap anterior and posterior labels when inconsistent with swimming direction.
        * `local_piv_analysis.py`: calculates circular mean of PIV angle near anterior and posterior ends.
        * `local_piv_analysis2.py`: calculates the mean angle near the anterior and posterior ends.
        * `piv.py`: produces velocity fields from image sequences.
        * `piv_analysis.py`: calculates circular mean and variance of PIV angle, frame by frame, and
        median velocity along cell axis.
        * `piv_density.py`: estimates the density of particles in a PIV movie.
        * `piv_movie.py`: makes an mp4 movie from the velocity fields.
        * `track_ends.py`: tracks the anterior and posterior ends of the cell.

The code is organized around a modular system of models that
can be combined together. Essentially, various models of currents and
calcium dynamics.
Each model is specified by equations, optimization bounds for
all optimized parameters, initial conditions (optional) and
a list of current variables names.

### Configuration
One must create a configuration file
`.paramecium_model_fitting.yaml`
in the home folder, following the model in `/file_management/`.

### Experiments
The script `experiment/current_pulses_experiment.py` can run a current pulse experiment with synchronized video.
It uses the `clampy` package. By default, it will run on an RC model (with no camera). To make it run on an
acquisition board and amplifier, you will need to edit the `init_rig.py` file (see the documentation of
`clampy`). The folder includes scripts to run a Lucam camera, this will need to be adapted to your camera.
The recording script sends trigger pulses through the acquisition board, which trigger frame acquisition.

### Complete pipeline for experimental data analysis with electrophysiology and PIV

1. The experiments produce data files: electrophysiology and images (.tiff).
2. Produce .mp4 movies with `scripts/data_preparation/make_movie.py`.
3. Designate anterior and posterior ends with `scripts/data_preparation/morphology.py`.
4. Calculate PIV with `scripts/image_analysis/piv.py`.
5. Analyze PIV data with `scripts/image_analysis/piv_analysis.py`.
6. Fix anterior/posterior positions with `scripts/image_analysis/fix_positions.py`.
7. Analyze local PIV with `scripts/image_analysis/local_piv_analysis.py`.
8. Track anterior/posterior movements with `scripts/image_analysis/track_ends.py`.
9. Analyze particle density with `scripts/analysis/sedimentation.py`.
10. Run a fitting script from `scripts/fitting/`.
11. Produce tables of fitting results with `scripts/data_preparation/make_tables`.
12. Select good cells with `scripts/analysis/selection_*.py`.
13. Display fits with `scripts/analysis/display_all_fits.py`.
14. Make figures from `scripts/figures/`.
