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
# For E-DPAs (West14, West13, East1, Webster Field)
#=========================================================================================

import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse

import sys
sys.path.append('../Spectrum-Access-System/src/harness')
import dpa_mgr_SEA as dpa_mgr

# Setup the command line arguments
parser = argparse.ArgumentParser(description='NASCTN SEA Modeling for E-DPAs')
parser.add_argument('--dpa_name', type=str, default='Webster Field',
                    help='The E-DPA name (e.g., East1, West14, West13, or Webster Field).')
INPUT = parser.parse_args()


def plotAggEmissionAtPrtnPointPerLoc(plot_dir, dpa_name, protected_points, channels,
                                     aggEmission_nbrList, aggEmission_keepList,
                                     noise_floor, prtn_threshold):
  """Plot aggregated emission at each protection point for all channels when the DPA is active/inactive.

  Inputs:
    plot_dir:               The directory to contain the plot(s).
    dpa_name:               The DPA name.
    protected_points:       A list of namedtuple (latitude, longitude) of the protection points.
    channels:               A list of tuple (low frequency, high frequency) of all channels.
    aggEmission_nbrList:    The aggregated emission when the DPA is inactive.
    aggEmission_keepList:   The aggreagted emission when the DPA is active.
    noise_floor:            Projected noise floor of sensor (dBm/10 MHz).
    prtn_threshold:         Protection threshold of the DPA (dBm/10 MHz).
    
  Returns:
    Plot(s) to be saved in the plot_dir folder.
  """
  channel_number = range(1, len(channels)+1)
  aggEmission_nbrList = np.array(aggEmission_nbrList)
  aggEmission_keepList = np.array(aggEmission_keepList)
  
  for i in range(len(protected_points)):
    fig, ax = plt.subplots(1, 1)
    plt.style.use('tableau-colorblind10')
  
    ax.plot(channel_number, aggEmission_nbrList[:, i], 'o', color='#ABABAB', label='DPA inactive (ref. ant.)')
    ax.plot(channel_number, aggEmission_keepList[:, i], '^', color='#595959', label='DPA active (ref. ant.)')
    plt.plot([channel_number[0]-1, channel_number[-1]+1], [noise_floor, noise_floor], 'k:', label='Noise floor')
    plt.plot([channel_number[0]-1, channel_number[-1]+1], [prtn_threshold, prtn_threshold], 'k--', label='Threshold')
  
    txt_size = 14
    ax.set_title('Protection point #'+str(i+1), fontsize=txt_size)
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
    plot_fname = plot_dir / (dpa_name+'_aggEmission_prtnPoint'+str(i+1)+'.png')
    plt.savefig(plot_fname)
    plt.close()


def plotAggEmissionAtPrtnPointPerCh(plot_dir, dpa_name, protected_points, channels,
                                    aggEmission_nbrList, aggEmission_keepList,
                                    noise_floor, prtn_threshold):
  """Plot aggregated emission at protection point(s) for each channel when the DPA is active/inactive.

  Inputs:
    plot_dir:               The directory to contain the plot(s).
    dpa_name:               The DPA name.
    protected_points:       A list of namedtuple (latitude, longitude) of the protection points.
    channels:               A list of tuple (low frequency, high frequency) of all channels.
    aggEmission_nbrList:    The aggregated emission when the DPA is inactive.
    aggEmission_keepList:   The aggreagted emission when the DPA is active.
    noise_floor:            Projected noise floor of sensor (dBm/10 MHz).
    prtn_threshold:         Protection threshold of the DPA (dBm/10 MHz).
    
  Returns:
    Plot(s) to be saved in the plot_dir folder.
  """
  pt_number = range(1, len(protected_points)+1)
  aggEmission_nbrList = np.array(aggEmission_nbrList)
  aggEmission_keepList = np.array(aggEmission_keepList)
  
  for i, channel in enumerate(channels):
    channel_str = 'channel'+str(channel[0])+'to'+str(channel[1])
    fig, ax = plt.subplots(1, 1)
    plt.style.use('tableau-colorblind10')
  
    ax.plot(pt_number, aggEmission_nbrList[i, :], 'o', color='#ABABAB', label='DPA inactive (ref. ant.)')
    ax.plot(pt_number, aggEmission_keepList[i, :], '^', color='#595959', label='DPA active (ref. ant.)')
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
    plot_fname = plot_dir / (dpa_name+'_'+channel_str+'_aggEmission_prtnPoint.png')
    plt.savefig(plot_fname)
    plt.close()


def plotAggEmissionAtSensorPerLoc(plot_dir, dpa_name, sensor_list, channels,
                                  aggEmission_nbrList, aggEmission_keepList,
                                  noise_floor, prtn_threshold):
  """Plot aggregated emission at each sensor location for all channels when the DPA is active/inactive.

  Inputs:
    plot_dir:               The directory to contain the plot(s).
    dpa_name:               The DPA name.
    sensor_list:            A list of namedtuple (index, location, latitude, longitude, 
                            height, antenna_filename, azimuth, downtilt) of the sensor locations.
    channels:               A list of tuple (low frequency, high frequency) of all channels.
    aggEmission_nbrList:    The aggregated emission when the DPA is inactive.
    aggEmission_keepList:   The aggreagted emission when the DPA is active.
    noise_floor:            Projected noise floor of sensor (dBm/10 MHz).
    prtn_threshold:         Protection threshold of the DPA (dBm/10 MHz).
    
  Returns:
    Plot(s) to be saved in the plot_dir folder.
  """
  channel_number = range(1, len(channels)+1)
  aggEmission_nbrList = np.array(aggEmission_nbrList)
  aggEmission_keepList = np.array(aggEmission_keepList)
  
  for i in range(len(sensor_list)):
    fig, ax = plt.subplots(1, 1)
    plt.style.use('tableau-colorblind10')
  
    ax.plot(channel_number, aggEmission_nbrList[:, i], 'o', color='#006BA4', label='DPA inactive')
    ax.plot(channel_number, aggEmission_keepList[:, i], '^', color='#FF800E', label='DPA active')
    plt.plot([channel_number[0]-1, channel_number[-1]+1], [noise_floor, noise_floor], 'k:', label='Noise floor')
    plt.plot([channel_number[0]-1, channel_number[-1]+1], [prtn_threshold, prtn_threshold], 'k--', label='Threshold')
  
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
    plot_fname = plot_dir / (dpa_name+'_aggEmission_sensorLocation'+str(i+1)+'.png')
    plt.savefig(plot_fname)
    plt.close()


def plotAggEmissionAtSensorPerCh(plot_dir, dpa_name, sensor_list, channels,
                                 aggEmission_nbrList, aggEmission_keepList,
                                 noise_floor, prtn_threshold):
  """Plot aggregated emission at sensor location(s) for each channel when the DPA is active/inactive.

  Inputs:
    plot_dir:               The directory to contain the plot(s).
    dpa_name:               The DPA name.
    sensor_list:            A list of namedtuple (index, location, latitude, longitude, 
                            height, antenna_filename, azimuth, downtilt) of the sensor locations.
    channels:               A list of tuple (low frequency, high frequency) of all channels.
    aggEmission_nbrList:    The aggregated emission when the DPA is inactive.
    aggEmission_keepList:   The aggreagted emission when the DPA is active.
    noise_floor:            Projected noise floor of sensor (dBm/10 MHz).
    prtn_threshold:         Protection threshold of the DPA (dBm/10 MHz).
    
  Returns:
    Plot(s) to be saved in the plot_dir folder.
  """
  pt_number = range(1, len(sensor_list)+1)
  aggEmission_nbrList = np.array(aggEmission_nbrList)
  aggEmission_keepList = np.array(aggEmission_keepList)
  
  for i, channel in enumerate(channels):
    channel_str = 'channel'+str(channel[0])+'to'+str(channel[1])
    fig, ax = plt.subplots(1, 1)
    plt.style.use('tableau-colorblind10')
  
    ax.plot(pt_number, aggEmission_nbrList[i, :], 'o', color='#006BA4', label='DPA inactive')
    ax.plot(pt_number, aggEmission_keepList[i, :], '^', color='#FF800E', label='DPA active')
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

    ax.legend(loc='upper right')
    plt.tight_layout()
    plot_fname = plot_dir / (dpa_name+'_'+channel_str+'_aggEmission_sensor.png')
    plt.savefig(plot_fname)
    plt.close()

def plotAggEmissionAtSensorUsingRefAntPerLoc(plot_dir, dpa_name, sensor_list, channels,
                                  aggEmission_nbrList, aggEmission_keepList,
                                  noise_floor, prtn_threshold):
  """Plot aggregated emission at each sensor location using reference antenna 
  for all channels when the DPA is active/inactive.

  Inputs:
    plot_dir:               The directory to contain the plot(s).
    dpa_name:               The DPA name.
    sensor_list:            A list of namedtuple (index, location, latitude, longitude, 
                            height, antenna_filename, azimuth, downtilt) of the sensor locations.
    channels:               A list of tuple (low frequency, high frequency) of all channels.
    aggEmission_nbrList:    The aggregated emission when the DPA is inactive.
    aggEmission_keepList:   The aggreagted emission when the DPA is active.
    noise_floor:            Projected noise floor of sensor (dBm/10 MHz).
    prtn_threshold:         Protection threshold of the DPA (dBm/10 MHz).
    
  Returns:
    Plot(s) to be saved in the plot_dir folder.
  """
  channel_number = range(1, len(channels)+1)
  aggEmission_nbrList = np.array(aggEmission_nbrList)
  aggEmission_keepList = np.array(aggEmission_keepList)
  
  for i in range(len(sensor_list)):
    fig, ax = plt.subplots(1, 1)
    plt.style.use('tableau-colorblind10')
  
    ax.plot(channel_number, aggEmission_nbrList[:, i], 'o', color='#ABABAB', label='DPA inactive (ref. ant.)')
    ax.plot(channel_number, aggEmission_keepList[:, i], '^', color='#595959', label='DPA active (ref. ant.)')
    plt.plot([channel_number[0]-1, channel_number[-1]+1], [noise_floor, noise_floor], 'k:', label='Noise floor')
    plt.plot([channel_number[0]-1, channel_number[-1]+1], [prtn_threshold, prtn_threshold], 'k--', label='Threshold')
  
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
    plot_fname = plot_dir / (dpa_name+'_aggEmission_sensorLocation'+str(i+1)+'_refAnt.png')
    plt.savefig(plot_fname)
    plt.close()


def plotAggEmissionAtSensorUsingRefAntPerCh(plot_dir, dpa_name, sensor_list, channels,
                                 aggEmission_nbrList, aggEmission_keepList,
                                 noise_floor, prtn_threshold):
  """Plot aggregated emission at sensor location(s) using reference antenna
  for each channel when the DPA is active/inactive.

  Inputs:
    plot_dir:               The directory to contain the plot(s).
    dpa_name:               The DPA name.
    sensor_list:            A list of namedtuple (index, location, latitude, longitude, 
                            height, antenna_filename, azimuth, downtilt) of the sensor locations.
    channels:               A list of tuple (low frequency, high frequency) of all channels.
    aggEmission_nbrList:    The aggregated emission when the DPA is inactive.
    aggEmission_keepList:   The aggreagted emission when the DPA is active.
    noise_floor:            Projected noise floor of sensor (dBm/10 MHz).
    prtn_threshold:         Protection threshold of the DPA (dBm/10 MHz).
    
  Returns:
    Plot(s) to be saved in the plot_dir folder.
  """
  pt_number = range(1, len(sensor_list)+1)
  aggEmission_nbrList = np.array(aggEmission_nbrList)
  aggEmission_keepList = np.array(aggEmission_keepList)
  
  for i, channel in enumerate(channels):
    channel_str = 'channel'+str(channel[0])+'to'+str(channel[1])
    fig, ax = plt.subplots(1, 1)
    plt.style.use('tableau-colorblind10')
  
    ax.plot(pt_number, aggEmission_nbrList[i, :], 'o', color='#ABABAB', label='DPA inactive (ref. ant.)')
    ax.plot(pt_number, aggEmission_keepList[i, :], '^', color='#595959', label='DPA active (ref. ant.)')
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

    ax.legend(loc='upper right')
    plt.tight_layout()
    plot_fname = plot_dir / (dpa_name+'_'+channel_str+'_aggEmission_sensor_refAnt.png')
    plt.savefig(plot_fname)
    plt.close()

if __name__ == '__main__':
  
  # DPA name and channels
  dpa_name = INPUT.dpa_name
  channels_start = list(range(3550, 3650, 10))
  channels_end = list(range(3560, 3660, 10))
  channels = list(zip(channels_start, channels_end))
  
  # Directories
  current_dir = Path.cwd()
  main_dir = Path(current_dir).parents[0]
  data_dir = main_dir / 'data'
  result_dir = main_dir / 'result' / dpa_name
  plot_dir = main_dir / 'plot' / dpa_name
  os.makedirs(plot_dir, exist_ok=True)
    
  # Predicted sensor noise floor
  noise_floor = -99         # Noise floor (dBm/10 MHz) (290 K, 5 dB NF)
  
  # Get DPA info
  dpa_mgr.Dpa.Configure()
  dpa_ref = dpa_mgr.BuildDpa(dpa_name)
  prtn_threshold = dpa_ref.threshold
  
  # Get aggregate emissions at protection points and sensor locations for all channels
  aggEmission_nbrList_prtnPt_allCh = []
  aggEmission_keepList_prtnPt_allCh = []
  aggEmission_nbrList_sensor_allCh = []
  aggEmission_keepList_sensor_allCh = []
  aggEmission_nbrList_sensor_refAnt_allCh = []
  aggEmission_keepList_sensor_refAnt_allCh = []
  for k, channel in enumerate(channels):
    channel_str = 'channel'+str(channel[0])+'to'+str(channel[1])
  
    # Get aggregate emission results at protection points
    fname = result_dir / (dpa_name+'_'+channel_str+'_aggEmission_prtnPoint.npy')
    (channel, protected_points, emission_nbrList_prtnPt, emission_keepList_prtnPt) = np.load(fname, allow_pickle=True)
    max_emission_nbrList_prtnPt = [np.amax(a) for a in np.array(emission_nbrList_prtnPt, dtype=object)] # Max value over all radar rotation azimuths
    max_emission_keepList_prtnPt = [np.amax(a) for a in np.array(emission_keepList_prtnPt, dtype=object)]
    aggEmission_nbrList_prtnPt_allCh.append(max_emission_nbrList_prtnPt)
    aggEmission_keepList_prtnPt_allCh.append(max_emission_keepList_prtnPt)

    # Get aggregate emission results at sensor locations
    fname = result_dir / (dpa_name+'_'+channel_str+'_aggEmission_sensor.npy')
    (channel, sensor_list, emission_nbrList_sensor, emission_keepList_sensor) = np.load(fname, allow_pickle=True)
    aggEmission_nbrList_sensor_allCh.append(emission_nbrList_sensor)
    aggEmission_keepList_sensor_allCh.append(emission_keepList_sensor)
  
    # Get aggregate emission results at sensor locations using reference antenna
    fname = result_dir / (dpa_name+'_'+channel_str+'_aggEmission_sensor_refAnt.npy')
    (channel, sensor_list, emission_nbrList_sensor_refAnt, emission_keepList_sensor_refAnt) = np.load(fname, allow_pickle=True)
    max_emission_nbrList_sensor_refAnt = [np.amax(a) for a in np.array(emission_nbrList_sensor_refAnt, dtype=object)] # Max value over all radar rotation azimuths
    max_emission_keepList_sensor_refAnt = [np.amax(a) for a in np.array(emission_keepList_sensor_refAnt, dtype=object)]
    aggEmission_nbrList_sensor_refAnt_allCh.append(max_emission_nbrList_sensor_refAnt)
    aggEmission_keepList_sensor_refAnt_allCh.append(max_emission_keepList_sensor_refAnt)
  
  # Plot aggregate emissions at protection points
  if len(protected_points)==1:
    plotAggEmissionAtPrtnPointPerLoc(plot_dir, dpa_name, protected_points, channels, 
                                     aggEmission_nbrList_prtnPt_allCh,
                                     aggEmission_keepList_prtnPt_allCh,
                                     noise_floor, prtn_threshold)
  else:
    plotAggEmissionAtPrtnPointPerCh(plot_dir, dpa_name, protected_points, channels,
                                    aggEmission_nbrList_prtnPt_allCh,
                                    aggEmission_keepList_prtnPt_allCh,
                                    noise_floor, prtn_threshold)

  # Plot aggregate emissions at sensor locations
  plotAggEmissionAtSensorPerLoc(plot_dir, dpa_name, sensor_list, channels,
                                aggEmission_nbrList_sensor_allCh,
                                aggEmission_keepList_sensor_allCh,
                                noise_floor, prtn_threshold)
  plotAggEmissionAtSensorPerCh(plot_dir, dpa_name, sensor_list, channels,
                               aggEmission_nbrList_sensor_allCh,
                               aggEmission_keepList_sensor_allCh,
                               noise_floor, prtn_threshold)
 
  # Plot aggregate emissions at sensor locations using reference azimuth antenna pattern
  plotAggEmissionAtSensorUsingRefAntPerLoc(plot_dir, dpa_name, sensor_list, channels,
                                           aggEmission_nbrList_sensor_refAnt_allCh,
                                           aggEmission_keepList_sensor_refAnt_allCh,
                                           noise_floor, prtn_threshold)
  plotAggEmissionAtSensorUsingRefAntPerCh(plot_dir, dpa_name, sensor_list, channels,
                                          aggEmission_nbrList_sensor_refAnt_allCh,
                                          aggEmission_keepList_sensor_refAnt_allCh,
                                          noise_floor, prtn_threshold)
