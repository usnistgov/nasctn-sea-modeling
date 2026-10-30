#    Copyright 2017 SAS Project Authors. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


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


"""Antenna gain routines for SAS.

Typical usage:
  # Get the gains for a given antenna horizontal pattern.
  # To be used for ESC and CBSD with actual antenna patterns.
  gains = GetAntennaPatternGains(hor_dirs, ant_azimuth, pattern)

  # Get CBSD antenna gain (from antenna defined by beamwidth and gain only).
  gains = GetStandardAntennaGains(hor_dirs, ant_azimuth, beamwidth, ant_gain)

  # Get Radar normalized antenna gain for DPA protection.
  gains = GetRadarNormalizedAntennaGains(hor_dirs, radar_azimuth)

  # Get FSS earth station antenna gains
  gains = GetFssAntennaGains(hor_dirs, ver_dirs,
                             fss_azimuth, fss_elevation, fss_ant_gain)
                             
  # Get SEA sensor 2D antenna gains
  gains = GetSensorAntennaGains(hor_dirs, ver_dirs,
                                ant_azimuth, ant_down_tilt,
                                frequency,
                                ant_gain_xarray)
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import xarray as xr


def GetAntennaPatternGains(hor_dirs, ant_azimuth,
                           hor_pattern,
                           ant_gain=0):
  """Computes the gain for a given antenna pattern.

  Directions and azimuth are defined compared to the north in clockwise
  direction and shall be within [0..360] degrees.

  Inputs:
    hor_dirs:       Ray directions in horizontal plane (degrees).
                    Either a scalar or an iterable.
    ant_azimuth:    Antenna azimuth (degrees).
    hor_pattern:    The antenna horizontal pattern defined as a ndarray of
                    360 values with the following conventions:
                     - clockwise increments of 1 degree.
                     - 0 degree corresponds to the antenna boresight.
                     - values are 'gain' (and not attenuation)
    ant_gain:       Optional additional antenna gain (dBi).
                    To be used if not included in the pattern (ie when using
                    a normalized pattern).

  Returns:
    The antenna gains (in dB): either a scalar if hor_dirs is scalar,
    or an ndarray otherwise.
  """
  is_scalar = np.isscalar(hor_dirs)
  hor_dirs = np.atleast_1d(hor_dirs)

  bore_angle = hor_dirs - ant_azimuth
  bore_angle[bore_angle >= 360] -= 360
  bore_angle[bore_angle < 0] += 360
  idx0 = bore_angle.astype(int)
  alpha = bore_angle - idx0
  idx1 = idx0 + 1
  idx1[idx1 >= 360] -= 360
  gains = (1-alpha) * hor_pattern[idx0] + alpha * hor_pattern[idx1]
  gains += ant_gain

  if is_scalar: return gains[0]
  return gains


def GetStandardAntennaGains(hor_dirs, ant_azimuth=None, ant_beamwidth=None, ant_gain=0):
  """Computes the antenna gains from a standard antenna defined by beamwidth.

  See R2-SGN-20.
  This uses the standard 3GPP formula for pattern derivation from a given
  antenna 3dB cutoff beamwidth.
  Directions and azimuth are defined compared to the north in clockwise
  direction and shall be within [0..360] degrees.

  Inputs:
    hor_dirs:       Ray directions in horizontal plane (degrees).
                    Either a scalar or an iterable.
    ant_azimut:     Antenna azimuth (degrees).
    ant_beamwidth:  Antenna 3dB cutoff beamwidth (degrees).
                    If None, then antenna is isotropic (default).
    ant_gain:       Antenna gain (dBi).

  Returns:
    The CBSD antenna gains (in dB).
    Either a scalar if hor_dirs is scalar or an ndarray otherwise.
  """
  is_scalar = np.isscalar(hor_dirs)
  hor_dirs = np.atleast_1d(hor_dirs)

  if (ant_beamwidth is None or ant_azimuth is None or
      ant_beamwidth == 0 or ant_beamwidth == 360):
    gains = ant_gain * np.ones(hor_dirs.shape)
  else:
    bore_angle = hor_dirs - ant_azimuth
    bore_angle[bore_angle > 180] -= 360
    bore_angle[bore_angle < -180] += 360
    gains = -12 * (bore_angle / float(ant_beamwidth))**2
    gains[gains < -20] = -20.
    gains += ant_gain

  if is_scalar: return gains[0]
  return gains


def GetRadarNormalizedAntennaGains(hor_dirs,
                                   radar_azimuth,
                                   radar_beamwidth=3):
  """Computes the DPA radar normalized antenna gain.

  See R2-SGN-24.
  Directions and azimuth are defined compared to the north in clockwise
  direction and shall be within [0..360] degrees.
  Note that the DPA antenna gain is normalized to 0dBi at boresight:
  actual radar antenna gain is implicitely included in the target interference
  thresholds.

  Inputs:
    hor_dirs:       Ray directions in horizontal plane (degrees).
                    Either a scalar or an iterable.
    radar_azimuth:  The radar antenna azimuth (degrees).
    radar_beamwidth: The radar antenna beamwidth (degrees).

  Returns:
    The normalized antenna gains (in dB).
    Either a scalar if hor_dirs is scalar or an ndarray otherwise.

  """
  if radar_beamwidth == 360:
    return 0.
  is_scalar = np.isscalar(hor_dirs)
  hor_dirs = np.atleast_1d(hor_dirs)

  bore_angle = hor_dirs - radar_azimuth
  bore_angle[bore_angle > 180] -= 360
  bore_angle[bore_angle < -180] += 360
  bore_angle = np.abs(bore_angle)
  gains = -25 * np.ones(len(bore_angle))
  gains[bore_angle < radar_beamwidth / 2.] = 0

  if is_scalar: return gains[0]
  return gains


def GetFssAntennaGains(hor_dirs, ver_dirs,
                       fss_pointing_azimuth, fss_pointing_elevation,
                       fss_antenna_gain,
                       w1=0, w2=1.0):
  """Computes the FSS earth station antenna gain.

  See R2-SGN-21.
  Horizontal directions and azimuth are defined compared to the north in
  clockwise fashion and shall be within [0..360] degrees.
  Vertical directions are positive for above horizon, and negative below.

  Inputs:
    hor_dirs:               Ray directions in horizontal plane (degrees).
                            Either a scalar or an iterable.
    ver_dirs:               Ray directions in vertical plane (degrees).
                            Either a scalar or an iterable (same dimension
                            as hor_dirs)
    fss_pointing_azimuth:   FSS earth station azimuth angle (degrees).
    fss_pointing_elevation: FSS earth station vertical angle (degrees).
    fss_antenna_gain:       FSS earth station nominal antenna gain (dBi).
    w1, w2:                 Weights on the tangent and perpendicular
                            components. Optional: by default only use the
                            perpendicular component.
  Returns:
    The FSS gains on the incoming ray (in dB).
    Either a scalar if hor_dirs is scalar, or an ndarray otherwise.
  """
  is_scalar = np.isscalar(hor_dirs)
  hor_dirs = np.atleast_1d(np.radians(hor_dirs))
  ver_dirs = np.atleast_1d(np.radians(ver_dirs))
  fss_pointing_elevation = np.radians(fss_pointing_elevation)
  fss_pointing_azimuth = np.radians(fss_pointing_azimuth)

  # Compute the satellite antenna off-axis angle - see formula in R2-SGN-21, iii
  theta = 180/np.pi * np.arccos(
      np.cos(ver_dirs) * np.cos(fss_pointing_elevation)
      * np.cos(fss_pointing_azimuth - hor_dirs) +
      np.sin(ver_dirs) * np.sin(fss_pointing_elevation))

  gain_gso_t, gain_gso_p = _GetGsoGains(theta, fss_antenna_gain)
  gains = w1 * gain_gso_t + w2 * gain_gso_p

  if is_scalar: return gains[0]
  return gains


def _GetGsoGains(theta, nominal_gain):
  """Returns FSS earth station gains from the off-axis angle.

  GSO means the 'Geostationary Satellite Orbit'.

  Inputs:
    theta:        Off-axis angles (degrees), as a ndarray
    nominal_gain: Nominal antenna gain (dBi)
  Returns:
    a tuple of ndarray:
      gain_gso_t: Gains in the tangent plane of the GSO (dB).
      gain_gso_p: Gains in the perpendicular plane of the GSO (dB).
  """
  theta = np.abs(theta)
  gain_gso_t = -10 * np.ones(len(theta))
  gain_gso_p = gain_gso_t.copy()

  gain_gso_p[theta <= 3] = nominal_gain
  idx_3_to_48 = np.where((theta > 3) & (theta <= 48))[0]
  gain_gso_p[idx_3_to_48] = 32 - 25 * np.log10(theta[idx_3_to_48])

  gain_gso_t[theta <= 1.5] = nominal_gain
  idx_1_5_to_7 = np.where((theta > 1.5) & (theta <= 7))[0]
  gain_gso_t[idx_1_5_to_7] = 29 - 25 * np.log10(theta[idx_1_5_to_7])
  gain_gso_t[(theta > 7) & (theta <= 9.2)] = 8
  idx_9_2_to_48 = np.where((theta > 9.2) & (theta <= 48))[0]
  gain_gso_t[idx_9_2_to_48] = 32 - 25 * np.log10(theta[idx_9_2_to_48])

  return gain_gso_t, gain_gso_p

  
def GetSensorAntennaGains(hor_dirs, ver_dirs, 
                          ant_azimuth, ant_down_tilt, 
                          frequency, 
                          ant_gain_xarray):
  """Computes sensor antenna gains.

  Horizontal directions and azimuth are defined compared to the north in
  clockwise fashion and shall be within [0..360] degrees.
  Vertical directions are positive for above horizon, and negative below.
  Frequency shall be within [3.55e9 .. 3.7e9]

  Inputs:
    hor_dirs:           Ray directions in horizontal plane (degrees).
                        Either a scalar or an iterable.
    ver_dirs:           Ray directions in vertical plane (degrees).
                        Either a scalar or an iterable (same dimension
                        as hor_dirs)
    ant_azimuth:        Sensor antenna azimuth angle (degrees).
    ant_down_tilt:      Sensor antenna vertical downtilt angle (degrees).
                        The angle is defined as positive down.
    frequency:          Operating frequency (Hz).
    ant_gain_xarray:    An xarray object containing antenna gain (dBi).
                        The object's dimensions are "frequency",
                        "azimuth", and "elevation".

  Returns:
    The sensor gains on the incoming ray (in dBi).
    Either a scalar if hor_dirs is scalar, or an ndarray otherwise.
  """
  is_scalar = np.isscalar(hor_dirs)

  # Convert to radians
  hor_dirs = np.deg2rad(np.atleast_1d(hor_dirs))
  ver_dirs = np.deg2rad(np.atleast_1d(ver_dirs))
  ant_azimuth = np.deg2rad(ant_azimuth)
  ant_down_tilt = np.deg2rad(ant_down_tilt)
  az_delta = ant_azimuth - hor_dirs

  # Get angles in local antenna coordinates
  local_azimuth = np.rad2deg(
    -np.arctan2(
          np.sin(az_delta), 
          np.cos(ant_down_tilt) * np.cos(az_delta) - np.sin(ant_down_tilt) * np.tan(ver_dirs)
    )
  )

  local_elevation = np.rad2deg(
    np.arcsin(
      np.sin(ant_down_tilt) * np.cos(ver_dirs) * np.cos(ant_azimuth - hor_dirs)
      + np.cos(ant_down_tilt) * np.sin(ver_dirs)
    )
  )

  # Get data at "(local_azimuth, local_elevation)"
  # using linear multidimensional interpolation
  azimuth = xr.DataArray(local_azimuth, dims="z")
  elevation = xr.DataArray(local_elevation, dims="z")
  da = ant_gain_xarray.interp(frequency=frequency, azimuth=azimuth, elevation=elevation)

  # Get gains
  gains = da.values

  if is_scalar:
    return gains[0]
  return gains

  