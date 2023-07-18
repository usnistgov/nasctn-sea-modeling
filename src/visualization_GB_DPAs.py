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
# For GB-DPAs (Camp Pendleton)
#=========================================================================================

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from pathlib import Path

import sys
sys.path.append('../Spectrum-Access-System/src/harness')
import dpa_mgr_SEA as dpa_mgr


def plotAggEmissionAtPrtnPointPerCh(plot_dir, dpa_names, protected_points, channels, 
                                    aggEmission_keepList, 
                                    noise_floor, prtn_threshold_list):
  """Plot aggregated emission at protection point(s) for each channel when the DPA is active/inactive.

  Inputs:
    plot_dir:               The directory to contain the plot(s).
    dpa_names:              A list of DPA names.
    protected_points:       A list of namedtuple (latitude, longitude) of the protection points.
    channels:               A list of tuple (low frequency, high frequency) of all channels.
    aggEmission_keepList:   The aggreagted emission when the DPA is active.
    noise_floor:            Projected noise floor of sensor (dBm/10 MHz).
    prtn_threshold_list:    A list of protection thresholds of the DPAs (dBm/10 MHz).
    
  Returns:
    Plot(s) to be saved in the plot_dir folder.
  """
  pt_number = range(1, len(protected_points)+1)
  aggEmission_keepList = np.array(aggEmission_keepList)
  
  for i, channel in enumerate(channels):
    channel_str = 'channel'+str(channel[0])+'to'+str(channel[1])
    fig, ax = plt.subplots(1, 1)
    plt.style.use('tableau-colorblind10')
    prtn_threshold = prtn_threshold_list[i]

    ax.plot(pt_number, aggEmission_keepList[i, :], '^', color='#FF800E', label='DPA always-on')
    plt.plot([pt_number[0]-1, pt_number[-1]+1], [noise_floor, noise_floor], 'k:', label='Noise floor')
    plt.plot([pt_number[0]-1, pt_number[-1]+1], [prtn_threshold, prtn_threshold], 'k--', label='Threshold')
  
    txt_size = 14
    ax.set_title('Channel '+str(i+1)+': ('+str(channel[0])+'-'+str(channel[1])+') MHz', fontsize=txt_size)
    ax.set_ylabel('Aggregate emission (dBm/10 MHz)', fontsize=txt_size)
    ax.set_xlabel('Protection point number', fontsize=txt_size)

    major_ytick = range(-180, 0, 20)
    ax.set_yticks(major_ytick)
    ax.grid(which='major', linestyle='-', alpha=0.5)
    ax.set_ylim(-180, 0)
    ax.set_xlim(pt_number[0]-1, pt_number[-1]+1)

    ax.legend(loc='upper right')
    plt.tight_layout()
    plot_fname = plot_dir / (dpa_names[i]+'_'+channel_str+'_aggEmission_prtnPoint.png')
    plt.savefig(plot_fname)
    plt.close()


def plotAggEmissionAtSensorPerLoc(plot_dir, dpa_names, sensor_list, channels, 
                                  aggEmission_keepList, noise_floor):
  """Plot aggregated emission at each sensor location for all channels when the DPA is active/inactive.

  Inputs:
    plot_dir:               The directory to contain the plot(s).
    dpa_names:              A list of DPA names.
    sensor_list:            A list of namedtuple (index, location, latitude, longitude, 
                            height, antenna_filename, azimuth, downtilt) of the sensor locations.
    channels:               A list of tuple (low frequency, high frequency) of all channels.
    aggEmission_keepList:   The aggreagted emission when the DPA is active.
    noise_floor:            Projected noise floor of sensor (dBm/10 MHz).
    
  Returns:
    Plot(s) to be saved in the plot_dir folder.
  """
  channel_number = range(1, len(channels)+1)
  aggEmission_keepList = np.array(aggEmission_keepList)
  
  for i in range(len(sensor_list)):
    fig, ax = plt.subplots(1, 1)
    plt.style.use('tableau-colorblind10')
    
    ax.plot(channel_number, aggEmission_keepList[:, i], '^', color='#FF800E', label='DPA always-on')
    plt.plot([channel_number[0]-1, channel_number[-1]+1], [noise_floor, noise_floor], 'k:', label='Noise floor')

    txt_size = 14
    ax.set_title('Sensor location #'+str(i+1), fontsize=txt_size)
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
    plot_fname = plot_dir / (dpa_names[i]+'_aggEmission_sensorLocation'+str(i+1)+'.png')
    plt.savefig(plot_fname)
    plt.close()


def plotAggEmissionAtSensorPerCh(plot_dir, dpa_names, sensor_list, channels, 
                                 aggEmission_keepList, 
                                 noise_floor, prtn_threshold_list):
  """Plot aggregated emission at sensor location(s) for each channel when the DPA is active/inactive.

  Inputs:
    plot_dir:               The directory to contain the plot(s).
    dpa_name:               The DPA name.
    sensor_list:            A list of namedtuple (index, location, latitude, longitude, 
                            height, antenna_filename, azimuth, downtilt) of the sensor locations.
    channels:               A list of tuple (low frequency, high frequency) of all channels.
    aggEmission_keepList:   The aggreagted emission when the DPA is active.
    noise_floor:            Projected noise floor of sensor (dBm/10 MHz).
    prtn_threshold_list:    A list of protection thresholds of the DPAs (dBm/10 MHz).
    
  Returns:
    Plot(s) to be saved in the plot_dir folder.
  """
  pt_number = range(1, len(sensor_list)+1)
  aggEmission_keepList = np.array(aggEmission_keepList)
  
  for i, channel in enumerate(channels):
    channel_str = 'channel'+str(channel[0])+'to'+str(channel[1])
    fig, ax = plt.subplots(1, 1)
    plt.style.use('tableau-colorblind10')
    prtn_threshold = prtn_threshold_list[i]

    ax.plot(pt_number, aggEmission_keepList[i, :], '^', color='#FF800E', label='DPA always-on')
    plt.plot([pt_number[0]-1, pt_number[-1]+1], [noise_floor, noise_floor], 'k:', label='Noise floor')
    plt.plot([pt_number[0]-1, pt_number[-1]+1], [prtn_threshold, prtn_threshold], 'k--', label='Threshold')
  
    txt_size = 14
    ax.set_title('Channel '+str(i+1)+': ('+str(channel[0])+'-'+str(channel[1])+') MHz', fontsize=txt_size)
    ax.set_ylabel('Aggregate emission (dBm/10 MHz)', fontsize=txt_size)
    ax.set_xlabel('Sensor location number', fontsize=txt_size)

    major_ytick = range(-180, 0, 20)
    ax.set_yticks(major_ytick)
    ax.grid(which='major', linestyle='-', alpha=0.5)
    ax.set_ylim(-180, 0)
    ax.set_xlim(pt_number[0]-1, pt_number[-1]+1)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    ax.legend(loc='upper right')
    plt.tight_layout()
    plot_fname = plot_dir / (dpa_names[i]+'_'+channel_str+'_aggEmission_sensor.png')
    plt.savefig(plot_fname)
    plt.close()


if __name__ == '__main__':
  
  # DPA names and channels
  dpa_main_name = 'MCBPendleton'
  dpa_names = []
  for i_dpa in range(1,11):
    dpa_names.append(dpa_main_name+'-'+f"{i_dpa:02}")
    
  channels_start = list(range(3550, 3650, 10))
  channels_end = list(range(3560, 3660, 10))
  channels = list(zip(channels_start, channels_end))
  
  # Directories
  current_dir = Path.cwd()
  main_dir = Path(current_dir).parents[0]
  data_dir = main_dir / 'data'
  result_dir = main_dir / 'result' / dpa_main_name
  plot_dir = main_dir / 'plot' / dpa_main_name
  os.makedirs(plot_dir, exist_ok=True)
    
  # Predicted sensor noise floor
  noise_floor = -99         # Noise floor (dBm/10 MHz) (290 K, 5 dB NF)
  
  # Get aggregate emissions at protection points and sensor locations for all channels
  aggEmission_keepList_prtnPt_allCh = []
  aggEmission_keepList_sensor_allCh = []
  prtn_threshold_allCh = []
  
  for i_dpa, dpa_name in enumerate(dpa_names):
    channel = channels[i_dpa]
    channel_str = 'channel'+str(channel[0])+'to'+str(channel[1])
    
    # Get DPA info
    dpa_mgr.Dpa.Configure()
    dpa_ref = dpa_mgr.BuildDpa(dpa_name)
    prtn_threshold = dpa_ref.threshold
    prtn_threshold_allCh.append(prtn_threshold)
  
    # Get aggregate emission results at protection points
    fname = result_dir / (dpa_name+'_'+channel_str+'_aggEmission_prtnPoint.npy')
    (channel, protected_points, emission_nbrList_prtnPt, emission_keepList_prtnPt) = np.load(fname, allow_pickle=True)
    max_emission_keepList_prtnPt = [np.amax(a) for a in np.array(emission_keepList_prtnPt)] # Max value over all radar rotation azimuths
    aggEmission_keepList_prtnPt_allCh.append(max_emission_keepList_prtnPt)

    # Get aggregate emission results at sensor locations
    fname = result_dir / (dpa_name+'_'+channel_str+'_aggEmission_sensor.npy')
    (channel, sensor_list, emission_nbrList_sensor, emission_keepList_sensor) = np.load(fname, allow_pickle=True)
    aggEmission_keepList_sensor_allCh.append(emission_keepList_sensor)
  
  # Plot aggregate emissions at protection points
  plotAggEmissionAtPrtnPointPerCh(plot_dir, dpa_names, protected_points, channels, aggEmission_keepList_prtnPt_allCh, noise_floor, prtn_threshold_allCh)

  # Plot aggregate emissions at all sensor locations for each channel
  plotAggEmissionAtSensorPerCh(plot_dir, dpa_names, sensor_list, channels, aggEmission_keepList_sensor_allCh, noise_floor, prtn_threshold_allCh)

