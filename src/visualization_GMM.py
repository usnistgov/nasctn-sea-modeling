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
# Script to plot NASCTN SEA modeling results
# For Green Mountain Mesa (GMM) sensor location.
#=========================================================================================

import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def plotAggEmissionAtSensor(plot_dir, loc_name, sensor, channels, aggEmission, noise_floor):
  """Plot aggregated emission at sensor location for all channels.

  Inputs:
    plot_dir:               The directory to contain the plot(s).
    loc_name:               The sensor location name.
    sensor:                 A namedtuple (index, location, latitude, longitude, 
                            height, antenna_filename, azimuth, downtilt) of the sensor locations.
    channels:               A list of tuple (low frequency, high frequency) of all channels.
    aggEmission :           The aggregated emission.
    noise_floor:            Projected noise floor of sensor (dBm/10 MHz).
    
  Returns:
    Plot(s) to be saved in the plot_dir folder.
  """
  channel_number = range(1, len(channels)+1)
  aggEmission = np.array(aggEmission)
  
  fig, ax = plt.subplots(1, 1)
  plt.style.use('tableau-colorblind10')
  
  ax.plot(channel_number, aggEmission, 'o', color='#006BA4', label='Agg. emission')
  plt.plot([channel_number[0]-1, channel_number[-1]+1], [noise_floor, noise_floor], 'k:', label='Noise floor')
  
  txt_size = 14
  ax.set_title(sensor.location+' sensor location', fontsize=txt_size)
  ax.set_ylabel('Aggregate emission (dBm/10 MHz)', fontsize=txt_size)
  ax.set_xlabel('Channel number', fontsize=txt_size)
  
  major_xtick = channel_number
  ax.set_xticks(major_xtick)
  ax.grid(which='major', linestyle='-', alpha=0.5)
  ax.set_xlim(major_xtick[0]-1, major_xtick[-1]+1)
  
  major_ytick = range(-180, 0, 20)
  ax.set_yticks(major_ytick)
  ax.grid(which='major', linestyle='-', alpha=0.5)
  ax.set_ylim(-180, 0)

  ax.legend(loc='upper right')
  plt.tight_layout()
  plot_fname = plot_dir / (loc_name+'_aggEmission_sensorLocation.png')
  plt.savefig(plot_fname)
  plt.close()


if __name__ == '__main__':
  
  # DPA name and channels
  loc_name = 'GMM'
  channels_start = list(range(3550, 3650, 10))
  channels_end = list(range(3560, 3660, 10))
  channels = list(zip(channels_start, channels_end))
  
  # Directories
  current_dir = Path.cwd()
  main_dir = Path(current_dir).parents[0]
  data_dir = main_dir / 'data'
  result_dir = main_dir / 'result' / loc_name
  plot_dir = main_dir / 'plot' / loc_name
  os.makedirs(plot_dir, exist_ok=True)
    
  # Predicted sensor noise floor
  noise_floor = -99         # Noise floor (dBm/10 MHz) (290 K, 5 dB NF)
  
  # Get aggregate emissions at protection points and sensor locations for all channels
  aggEmission_allCh = []

  for k, channel in enumerate(channels):
    channel_str = 'channel'+str(channel[0])+'to'+str(channel[1])

    # Get aggregate emission results at sensor locations
    fname = result_dir / (loc_name+'_'+channel_str+'_aggEmission_sensor.npy')
    (channel, sensor, agg_emission) = np.load(fname, allow_pickle=True)
    aggEmission_allCh.append(agg_emission)

  # Plot aggregate emissions at sensor location
  plotAggEmissionAtSensor(plot_dir, loc_name, sensor, channels, aggEmission_allCh, noise_floor)

 
