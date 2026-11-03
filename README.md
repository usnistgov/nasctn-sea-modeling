# NASCTN SEA Modeling Repository

This repository contains code used in the modeling for the National Advanced Spectrum and Communications Test Network (NASCTN) Sharing Ecosystem Assessment (SEA) project. It runs dynamic protection area (DPA) move list algorithm and computes aggregate emission at protection points and sensor locations in the Citizens Broadband Radio Service (CBRS) band. Some of the scripts were derived from the WInnForum's reference implementation of the Spectrum Access System (SAS) test harness.

## Data

The data required to run the code need to be stored in the `data/` folder, which contains `fad/` and `sensor/` subfolders:
* The `fad/` subfolder contains information of Citizens Broadband Radio Service Device (CBSD) grants, which can be extracted from real Full Activity Dump (FAD) data files. The current `fad/` subfolder is empty due to propriety information.
* The `sensor/` subfolder contains information of SEA sensors (e.g., location, height, 2D antenna data, etc.) and associated 2D antenna gain .nc files.

## Code prerequisites

The code in this repository depend on the WInnForum's SAS test harness code and data. In order to run the code correctly, it's required to:
* Install all the packages and software listed at [https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System](https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System)
* Download the geo data (e.g., USGS NED Terrain and NLCD Land cover data, etc. ) by following the instructions at [https://github.com/Wireless-Innovation-Forum/Common-Data](https://github.com/Wireless-Innovation-Forum/Common-Data) 
* Set up and compile extension modules for propagation models by following the instructions at [https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System/tree/master/src/harness/reference_models/propagation](https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System/tree/master/src/harness/reference_models/propagation)
* Download *e-dpas.kml* and *gb-dpas.kml* file from ([https://www.ntia.gov/spectrum-frequency-bands/3550-3650-mhz](https://www.ntia.gov/spectrum-frequency-bands/3550-3650-mhz)) and save them under `../Spectrum-Access-System/data/ntia/` folder
* Install *xarray* package and its dependencies ([https://docs.xarray.dev/en/stable/getting-started-guide/installing.html](https://docs.xarray.dev/en/stable/getting-started-guide/installing.html))
* Install *scipy* package ([https://scipy.org/install/](https://scipy.org/install/))

  Note: Validating the setup using the `test_config.py` under `../Spectrum-Access-System/src/harness/reference_models` folder might produce error messages for missing NED terrain tiles or missing NLCD land cover. However, these error messages might not affect the execution of NASCTN SEA modeling code.

## Usage

1. Clone this repository:

   ```bash
   git clone https://github.com/usnistgov/nasctn-sea-modeling
   ```

2. Update the `../Spectrum-Access-System/src/harness` folder with local directory in the following scripts:

 ```bash
   src/mainscript_E_DPAs.py
   src/mainscript_GB_DPAs.py
   visualization/cbsd_grant_list_analysis_E_DPAs.ipynb
   visualization/cbsd_grant_list_analysis_GB_DPAs.ipynb
   visualization/aggregate_emission_analysis_E_DPAs.ipynb
   visualization/aggregate_emission_analysis_GB_DPAs.ipynb
   ```

   Note that `visualization/*.ipynb` scripts are optional, which can used for plotting the results for a specific DPA.

3. Configure the number of parallel processes, i.e., `num_processes` parameter, in the following scripts `src/mainscript_E_DPAs.py` and `src/mainscript_GB_DPAs.py`.

4. Navigate to the `src/` folder and type the following commands to run move list algorithm and compute aggregate emission at protection points and SEA sensor locations:

   ```python
   ########## For E-DPAs (e.g., East1) ##########
   python mainscript_E_DPAs.py --dpa_name="East1"

   ########## For GB-DPAs (always-on DPA Camp Pendleton) ##########
   python mainscript_GB_DPAs.py --dpa_name="MCBPendleton"

   ########## For multiple DPAs: edit and run Bash scripts ##########
   bash mainscript_bash.sh 
   ```

5. Navigate to the `visualization/` folder and use the following notebooks to plot the results:

   ```python
   ########## For E-DPAs (e.g., East1) ##########
   # plot and save CBSD grant lists 
   cbsd_grant_list_analysis_E_DPAs.ipynb

   # plot aggregate emissions at protection points and sensor locations
   aggregate_emission_analysis_E_DPAs.ipynb

   ########## For GB-DPAs (always-on DPA Camp Pendleton) ##########
   # plot and save CBSD grant lists 
   cbsd_grant_list_analysis_GB_DPAs.ipynb

   # plot aggregate emissions at protection points and sensor locations
   aggregate_emission_analysis_GB_DPAs.ipynb
   ```

## NIST Software Licensing Statement

NIST-developed software is provided by NIST as a public service. You may use, copy, and distribute copies of the software in any medium, provided that you keep intact this entire notice. You may improve, modify, and create derivative works of the software or any portion of the software, and you may copy and distribute such modifications or works. Modified works should carry a notice stating that you changed the software and should note the date and nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the source of the software.

NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED, IN FACT, OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE.

You are solely responsible for determining the appropriateness of using and distributing the software and you assume all risks associated with its use, including but not limited to the risks and costs of program errors, compliance with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of operation. This software is not intended to be used in any situation where a failure could cause risk of injury or damage to property. The software developed by NIST employees is not subject to copyright protection within the United States.

NIST software license disclaimer can be found at: https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications#software

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

We would like to thank our colleagues and individuals (from NIST/CTL, NTIA/ITS, MITRE, and other stakeholders) that made valuable contributions to the code and data in this repository.

## Contact information

Thao Nguyen (thao.t.nguyen@nist.gov).


