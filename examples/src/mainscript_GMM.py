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
# To compute aggregate emission from CBSD grants to Green Mountain Mesa (GMM)
# sensor location.
#=========================================================================================

import os
import time
import numpy as np
from pathlib import Path
import json

import sys
sys.path.append('/raid/Spectrum-Access-System/src/harness') # NOTE: Use your local directory
import data_SEA as data
import move_list_SEA as ml
import utils_SEA as utils
from reference_models.geo import vincenty


if __name__ == '__main__':
  
  start_time = time.time()
  
  # DPA name and channels
  loc_name = 'GMM'
  print('Sensor location: ' + loc_name)
  channels_start = list(range(3550, 3650, 10))
  channels_end = list(range(3560, 3660, 10))
  channels = list(zip(channels_start, channels_end))
  
  # Directories
  current_dir = Path.cwd()
  main_dir = Path(current_dir).parents[0]
  data_dir = main_dir / 'data'
  fad_dir = data_dir / 'fad'
  sensor_dir = data_dir / 'sensor'
  result_dir = main_dir / 'result' / loc_name
  os.makedirs(result_dir, exist_ok=True)
  
  # Read sensor data
  sensor_filename = sensor_dir / (loc_name + '_sensor.csv')
  sensor_list = utils.readSensorData(sensor_filename)
  sensor = sensor_list[0]
  print('Sensor data: ', sensor)

  # Number of Monte Carlo iterations
  num_iter = 2000
  
  # Read grant data from .json file
  cbsd_data_records = utils.readCbsdGrantData(fad_dir)
  grants = data.getAllGrantInfoFromCbsdDataDump(cbsd_data_records)
  print('Number of grants:', len(grants))
  
  # Loop over each CBSD grant and filter the ones inside the neighborhood of sensor
  nbr_dist_km = 200     # Estimated distance
  grants_inside = []
  for k, grant in enumerate(grants):
    # Compute distance from CBSD location to sensor location
    dist_km, _, _ = vincenty.GeodesicDistanceBearing(
        grant.latitude, grant.longitude,
        sensor.latitude, sensor.longitude)    
    # Check if CBSD is inside the neighborhood of sensor location
    if dist_km > nbr_dist_km:
      continue
    grants_inside.append(grant)
  print('Number of grants inside neighborhood:', len(grants_inside))
  
  # Loop over each channel
  for channel in channels:
    print('')
    print('Channel: ' + str(channel))
    channel_str = 'channel'+str(channel[0])+'to'+str(channel[1])
    
    # Find grants operate on the channel
    grants_on_channel = [g for g in grants_inside
            if (min(g.high_frequency, channel[1] * 1.e6) - max(g.low_frequency, channel[0] * 1.e6)) > 0]
    print('Number of grants on the channel:', len(grants_on_channel))
    
    # Compute aggregated emissions at sensor location
    agg_emission = ml.calcAggEmissionAtSensor(sensor=sensor,
                                              sensor_dir=sensor_dir,
                                              low_freq=channel[0] * 1e6,
                                              high_freq=channel[1] * 1e6,
                                              grants=grants_on_channel, 
                                              num_iter=num_iter)
    print('Aggregated emission: ' + str(agg_emission))
    fname = result_dir / (loc_name+'_'+channel_str+'_aggEmission_sensor.npy')
    np.save(fname, np.array([channel, sensor, agg_emission], dtype=object))

  end_time = time.time()
  print('Computation time: ' + str(end_time - start_time))

