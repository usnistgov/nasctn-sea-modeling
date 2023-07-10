# This software was developed by employees of the National Institute
# of Standards and Technology (NIST), an agency of the Federal
# Government. Pursuant to title 17 United States Code Section 105, works
# of NIST employees are not subject to copyright protection in the United
# States and are considered to be in the public domain. Permission to freely
# use, copy, modify, and distribute this software and its documentation
# without fee is hereby granted, provided that this notice and disclaimer
# of warranty appears in all copies.
#
# THE SOFTWARE IS PROVIDED 'AS IS' WITHOUT ANY WARRANTY OF ANY KIND,
# EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED
# TO, ANY WARRANTY THAT THE SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
# AND FREEDOM FROM INFRINGEMENT, AND ANY WARRANTY THAT THE DOCUMENTATION
# WILL CONFORM TO THE SOFTWARE, OR ANY WARRANTY THAT THE SOFTWARE WILL BE
# ERROR FREE. IN NO EVENT SHALL NIST BE LIABLE FOR ANY DAMAGES, INCLUDING,
# BUT NOT LIMITED TO, DIRECT, INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES,
# ARISING OUT OF, RESULTING FROM, OR IN ANY WAY CONNECTED WITH THIS
# SOFTWARE, WHETHER OR NOT BASED UPON WARRANTY, CONTRACT, TORT, OR
# OTHERWISE, WHETHER OR NOT INJURY WAS SUSTAINED BY PERSONS OR PROPERTY
# OR OTHERWISE, AND WHETHER OR NOT LOSS WAS SUSTAINED FROM, OR AROSE OUT
# OF THE RESULTS OF, OR USE OF, THE SOFTWARE OR SERVICES PROVIDED HEREUNDER.
#
# Distributions of NIST software should also include copyright and licensing
# statements of any third-party software that are legally bundled with
# the code in compliance with the conditions of those licenses.

#=========================================================================================
# Main script to run NASCTN SEA modeling
# To compute aggregate emission from CBSD grants to protection points and sensor locations
# For E-DPAs (West14, West13, East1, Webster Field)
#=========================================================================================

import os
import time
import numpy as np
from pathlib import Path
import argparse
import json

import sys
sys.path.append('../Spectrum-Access-System/src/harness') # NOTE: Use your local directory
from reference_models.common import mpool
import data_SEA as data
import dpa_mgr_SEA as dpa_mgr
import utils_SEA as utils

# Setup the command line arguments
parser = argparse.ArgumentParser(description='NASCTN SEA Modeling for E-DPAs')
parser.add_argument('--dpa_name', type=str, default='Webster Field',
                    help='The E-DPA name (e.g., East1, West14, West13, or Webster Field).')
INPUT = parser.parse_args()


if __name__ == '__main__':
  
  start_time = time.time()
  
  # DPA name and channels
  dpa_name = INPUT.dpa_name
  print('DPA: ' + dpa_name)
  channels_start = list(range(3550, 3650, 10))
  channels_end = list(range(3560, 3660, 10))
  dpa_channels = list(zip(channels_start, channels_end))
  
  # Directories
  current_dir = Path.cwd()
  main_dir = Path(current_dir).parents[0]
  data_dir = main_dir / 'data'
  fad_dir = data_dir / 'fad'
  sensor_dir = data_dir / 'sensor'
  result_dir = main_dir / 'result' / dpa_name
  os.makedirs(result_dir, exist_ok=True)
  
  # Sensor filename
  sensor_filename = sensor_dir / (dpa_name + '_sensor.csv')

  # Number of Monte Carlo iterations
  num_iter = 2000

  # Configure the global pool manager
  num_processes = 18    # NOTE: Configure number of parallel processes based on local machine capabilities
  mpool.Configure(num_processes)
  
  # Configure operating parameters
  dpa_mgr.Dpa.Configure(num_iteration=num_iter)
  
  # Apply similar protection point laydowns which were used by NTIA/ITS for SAS certification
  if "East" in dpa_name:
    dpa_ref = dpa_mgr.BuildDpa(dpa_name, protection_points_method='default (1e9, 1e9, 25, 25, 50, 5, 5, 10, 10)')
  else:
    dpa_ref = dpa_mgr.BuildDpa(dpa_name, protection_points_method='default (1e9, 1e9, 1e9, 1e9, 50, 5, 5, 10, 10)')
  print('Number of protection points:', len(dpa_ref.protected_points))
  
  # Read grant data from .json file and set them to DPA manager
  cbsd_data_records = utils.readCbsdGrantData(fad_dir)
  grants = data.getAllGrantInfoFromCbsdDataDump(cbsd_data_records)
  dpa_ref.SetGrantsFromList(grants)
  print('Number of grants:', len(grants))
  
  # Compute move list
  print('Compute move list ...')
  start_time = time.time()
  dpa_ref.ComputeMoveLists()
  end_time = time.time()  
  print('Computation time: ' + str(end_time - start_time))
  
  # Read sensor data
  sensor_list = utils.readSensorData(sensor_filename)
  
  # Loop over each dpa_channel
  for dpa_channel in dpa_channels:
    print('')
    print('DPA channel: ' + str(dpa_channel))
  
    # Get neighbor list
    neighborList = dpa_ref.GetNeighborList(dpa_channel)
    # Get move list
    moveList = dpa_ref.GetMoveList(dpa_channel)
    # Get keep list
    keepList = dpa_ref.GetKeepList(dpa_channel)
    print('Neighbor list size:', len(neighborList))
    print('Move list size:', len(moveList))
    print('Keep list size: ', len(keepList))
    dpa_channel_str = 'channel'+str(dpa_channel[0])+'to'+str(dpa_channel[1])

    # Compute aggregate emissions at protection points inside DPA using reference azimuth antenna pattern
    print('Compute aggregate emissions at protection points inside DPA using reference azimuth antenna pattern')
    emission_nbrList_prtnPt = dpa_ref.CalcAggEmissionAtPrtnPoint(dpa_channel, grants=neighborList, do_max=False)
    emission_keepList_prtnPt = dpa_ref.CalcAggEmissionAtPrtnPoint(dpa_channel, grants=keepList, do_max=False)
    fname = result_dir / (dpa_name+'_'+dpa_channel_str+'_aggEmission_prtnPoint.npy')
    np.save(fname, np.array([dpa_channel, dpa_ref.protected_points, emission_nbrList_prtnPt, emission_keepList_prtnPt], dtype=object))

    # Compute aggregate emissions at candidate sensor locations using 2D antenna patterns
    print('Compute aggregate emissions at sensor locations using 2D antenna patterns')
    emission_nbrList_sensor = dpa_ref.CalcAggEmissionAtSensor(dpa_channel, sensor_list, sensor_dir, grants=neighborList)
    emission_keepList_sensor = dpa_ref.CalcAggEmissionAtSensor(dpa_channel, sensor_list, sensor_dir, grants=keepList)
    fname = result_dir / (dpa_name+'_'+dpa_channel_str+'_aggEmission_sensor.npy')
    np.save(fname, np.array([dpa_channel, sensor_list, emission_nbrList_sensor, emission_keepList_sensor], dtype=object))

  end_time = time.time()
  print('Computation time: ' + str(end_time - start_time))
