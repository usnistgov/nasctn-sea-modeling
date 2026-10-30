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

#======================================================
# Utilities used for NASCTN SEA modeling
#======================================================

import json
from copy import deepcopy
import pandas
import warnings
from collections import namedtuple
import os
from pathlib import Path
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


# Define sensor information as a tuple with given named fields 
SensorInfo = namedtuple('SensorInfo', ['index', 'sensor_short_name', 'sensor_long_name',
                                       'location', 'latitude', 'longitude', 'height', 'height_type',
                                       'antenna_filename', 'azimuth', 'downtilt', 
                                       'noise_floor_dbm_per_mhz'])

def readCbsdGrantData(fad_dir, filename_str=None):
  """Read CBSD grant data from FAD files.
  
  Args:
    fad_dir: a directory contains all FAD files.
    filename_str: a string in the filename indicating it contains CBSD grants.
    
  Returns:
    cbsd_data_records: a list of CBSD grant records from all FAD CBSD files.
  """

  cbsd_data_records = []
  for file in Path(fad_dir).rglob('*.json'):
    if (filename_str is not None) and (filename_str in file.name):
      with open(file) as fp:
        fad_data = json.load(fp)
      cbsd_data_records.extend(fad_data['recordData'])
    else:
      with open(file) as fp:
        fad_data = json.load(fp)
      cbsd_file=False
      if 'recordData' in fad_data:
        record_data = fad_data['recordData']
        for record in record_data: 
          if 'grants' in record:
            cbsd_file=True
            break
      if cbsd_file:
        cbsd_data_records.extend(record_data)
  return cbsd_data_records


def readSensorData(sensor_filename):
  """Return a list of sensor data read from .csv file.

  Args:
    sensor_filename: sensor .csv filename

  Returns:
    sensor_list: a list of sensor data
  """
  
  sensor_list = []  
  # Read sensor data from csv file
  df = pandas.read_csv(sensor_filename, encoding= 'unicode_escape')
  df = df.reset_index() 
  for i, row in df.iterrows():
    sensor_list.append(SensorInfo(index=float(row['Index']),
      sensor_short_name=row['Sensor Short Name'],
      sensor_long_name=row['Sensor Long Name'],
      location=row['Location'],
      latitude=float(row['Latitude']),
      longitude=float(row['Longitude']),
      height=float(row['Height (m)']),
      height_type=row['Height Type'],
      antenna_filename=row['Antenna Filename'],
      azimuth=float(row['Antenna Azimuth']),
      downtilt=float(row['Antenna Downtilt']),
      noise_floor_dbm_per_mhz=float(row['Noise Floor (dBm/MHz)'])))
  return sensor_list

  
def csvToRegGrants(grant_filename, reg_request_filename, grant_request_filename):
  """Return lists of registration and grant requests from CBSD grant deployment csv file.

  Args:
    grant_filename: CBSD grant deployment csv filename
    reg_request_filename: template registration request json filename
    grant_request_filename: template grant request json filename

  Returns:
    reg_request_list: a list of registration request
    grant_request_list: a list of grant request
  """
  
  reg_request_list = []
  grant_request_list = []

  # Load template registration and grant requests
  reg_requestN = json.load(open(reg_request_filename))
  grant_requestN = json.load(open(grant_request_filename))
  
  # Read CBSD grant deployment csv file
  df = pandas.read_csv(grant_filename, encoding= 'unicode_escape')
  df = df.reset_index() 
  for i, row in df.iterrows():
    reg_request = deepcopy(reg_requestN)
    reg_request['fccId'] = '321cba_' + str(i+1)
    cbsdCategory = row['CBSD Category']
    if cbsdCategory=='Category_A' or cbsdCategory=='Category_B':
      reg_request['cbsdCategory'] = cbsdCategory[-1] # 'A' or 'B'
      reg_request['airInterface']['radioTechnology'] = row['Air Interface']
      reg_request['installationParam']['latitude'] = float(row['Latitude'])
      reg_request['installationParam']['longitude'] = float(row['Longitude'])
      reg_request['installationParam']['heightType'] = row['Height Type']
      reg_request['installationParam']['height'] = float(row['Height (m)'])
      reg_request['installationParam']['indoorDeployment'] = row['Indoor']
      reg_request_list.append(reg_request)
    
      grant_request = deepcopy(grant_requestN)
      grant_request['cbsdId'] = 'sas1/cbsd' + str(i+1)
      grant_request['operationParam']['maxEirp'] = float(row['maxEirp (dBm/MHz)'])
      grant_request['operationParam']['operationFrequencyRange']['lowFrequency'] = float(row['Low Frequency (Hz)'])
      grant_request['operationParam']['operationFrequencyRange']['highFrequency'] = float(row['High Frequency (Hz)'])
      grant_request_list.append(grant_request)
    
    else:
      warnings.warns(f"Unknown CBSD category: {row}")

  return reg_request_list, grant_request_list


def csvToRegGrantsInsideBuffer(grant_filename, reg_request_filename, grant_request_filename, dpa_buffer):
  """Return lists of registration and grant requests from CBSD grant deployment csv file.

  Args:
    grant_filename: CBSD grant deployment csv filename
    reg_request_filename: template registration request json filename
    grant_request_filename: template grant request json filename
    dpa_buffer: buffering of DPA 

  Returns:
    reg_request_list: a list of registration request
    grant_request_list: a list of grant request
  """
  
  reg_request_list = []
  grant_request_list = []

  # Load template registration and grant requests
  reg_requestN = json.load(open(reg_request_filename))
  grant_requestN = json.load(open(grant_request_filename))
  
  # Read CBSD grant deployment csv file
  df = pandas.read_csv(grant_filename, encoding= 'unicode_escape')
  df = df.reset_index() 
  for i, row in df.iterrows():
    reg_request = deepcopy(reg_requestN)
    reg_request['fccId'] = '321cba_' + str(i+1)
    cbsdCategory = row['CBSD Category']
    if cbsdCategory=='Category_A' or cbsdCategory=='Category_B':
      point = Point(float(row['Longitude']), float(row['Latitude']))
      if dpa_buffer.contains(point):
        reg_request['cbsdCategory'] = cbsdCategory[-1] # 'A' or 'B'
        reg_request['airInterface']['radioTechnology'] = row['Air Interface']
        reg_request['installationParam']['latitude'] = float(row['Latitude'])
        reg_request['installationParam']['longitude'] = float(row['Longitude'])
        reg_request['installationParam']['heightType'] = row['Height Type']
        reg_request['installationParam']['height'] = float(row['Height (m)'])
        reg_request['installationParam']['indoorDeployment'] = row['Indoor']
        reg_request_list.append(reg_request)
    
        grant_request = deepcopy(grant_requestN)
        grant_request['cbsdId'] = 'sas1/cbsd' + str(i+1)
        grant_request['operationParam']['maxEirp'] = float(row['maxEirp (dBm/MHz)'])
        grant_request['operationParam']['operationFrequencyRange']['lowFrequency'] = float(row['Low Frequency (Hz)'])
        grant_request['operationParam']['operationFrequencyRange']['highFrequency'] = float(row['High Frequency (Hz)'])
        grant_request_list.append(grant_request)
    
    else:
      warnings.warns(f"Unknown CBSD category: {row}")

  return reg_request_list, grant_request_list