"""
author: Andrei Militaru
organization: Institute of Science and Technology Austria (ISTA)
date: October 2025
Description: Utilities for locking a Mach-Zehnder interferometer using Zurich Instruments devices.
I will be adding utilities as time passes based on what we need.
"""

import numpy as np

# Default parameters for the piezo and laser locks as of 3rd October 2025
default_piezo_parameters = [0, 1e3, 0]
default_laser_parametrs = [-100e-3, -15e-3, 0]

def df2tc(freq):
    """
    Convert demodulator bandwidth to time constant for Zurich Instruments lock-in.
    
    Args:
        freq (float): Bandwidth frequency in Hz
    
    Returns:
        float: Time constant in seconds
    """
    return 1/(2*np.pi*freq)


def set_demodulators(mdrec, dev='dev30794', oscillator=0, demodulator=1, order=1, rate=53.57e3, bandwidth=20e3):
    """
    Configure demodulator settings for the Zurich Instruments lock-in amplifier.
    
    Args:
        mdrec: Demodulation recorder instance
        dev (str): Device ID
        oscillator (int): Oscillator index
        demodulator (int): Demodulator index
        order (int): Filter order
        rate (float): Sampling rate in Hz
        bandwidth (float): Demodulator bandwidth in Hz
    """
    mdrec.lock_in.set('/{:s}/oscs/{:d}/freq'.format(dev, oscillator), 0.)
    mdrec.lock_in.set('/{:s}/demods/{:d}/oscselect'.format(dev, demodulator), oscillator)
    mdrec.lock_in.set('/{:s}/demods/{:d}/adcselect'.format(dev, demodulator), 0)
    mdrec.lock_in.set('/{:s}/demods/{:d}/order'.format(dev, demodulator), order)
    mdrec.lock_in.set('/{:s}/demods/{:d}/timeconstant'.format(dev, demodulator), df2tc(bandwidth))
    mdrec.lock_in.set('/{:s}/demods/{:d}/rate'.format(dev, demodulator), rate)
    mdrec.lock_in.set('/{:s}/demods/{:d}/enable'.format(dev, demodulator), 1)
    mdrec.set_demod_list({'signal': (dev, 0)})


def set_aux_limits(mdrec, dev='dev30794', aux_lim=None, laser_lim=None):
    """
    Set the limits for auxiliary outputs controlling piezo and laser.
    
    Args:
        mdrec: Demodulation recorder instance
        dev (str): Device ID
        aux_lim (list): [min, max] voltage limits for piezo auxiliary output
        laser_lim (list): [min, max] voltage limits for laser auxiliary output
    """
    if aux_lim is None:
        aux_lim = [0, 5]
    if laser_lim is None:
        laser_lim = [-0.1, 0.1]
    mdrec.lock_in.set('/{:s}/auxouts/0/limitlower'.format(dev), aux_lim[0])
    mdrec.lock_in.set('/{:s}/auxouts/0/limitupper'.format(dev), aux_lim[1])
    mdrec.lock_in.set('/{:s}/auxouts/0/offset'.format(dev), (aux_lim[0] + aux_lim[1])/2)
    mdrec.lock_in.set('/{:s}/auxouts/3/offsetmin'.format(dev), laser_lim[0])
    mdrec.lock_in.set('/{:s}/auxouts/3/limitupper'.format(dev), laser_lim[1])
    mdrec.lock_in.set('/{:s}/auxouts/3/offset'.format(dev), 0)


def check_locks(mdrec, dev='dev30794', channels=None):
    """
        Check if the lock offsets are within acceptable ranges and reset them if they are not.
        The assumption is that the piezo channel is controlled via auxout 0 and the laser channel via auxout 3.
    
        Args:
            mdrec: Demodulation recorder instance
            dev (str): Device ID
            channels (list): List of channels to check ('piezo', 'laser')
    """
    if channels is None:
        channels = ['piezo', 'laser']
    if 'aux' in channels:
        val = mdrec.lock_in.getDouble('/{:s}/auxouts/0/offset'.format(dev))
        if not 0.3 < val < 4.7:
            mdrec.lock_in.setInt('/{:s}/pids/0/enable'.format(dev), 0)
            mdrec.lock_in.setDouble('/{:s}/auxouts/0/offset'.format(dev), 2.5)
            mdrec.lock_in.setInt('/{:s}/pids/0/enable'.format(dev), 1)
    if 'laser' in channels:
        val = mdrec.lock_in.getDouble('/{:s}/auxouts/3/offset'.format(dev))
        if not -80e-3 < val < 80e-3:
            mdrec.lock_in.setInt('/{:s}/pids/3/enable'.format(dev), 0)
            mdrec.lock_in.setDouble('/{:s}/auxouts/3/offset'.format(dev), 0)
            mdrec.lock_in.setInt('/{:s}/pids/3/enable'.format(dev), 1)


def set_setpoint(mdrec, new_value, dev='dev30794'):
    """
    Set the PID controller setpoints for both piezo and laser channels.
    
    Args:
        mdrec: Demodulation recorder instance
        new_value (float): New setpoint value
        dev (str): Device ID
    """
    mdrec.lock_in.set('/{:s}/pids/0/setpoint', new_value)
    mdrec.lock_in.set('/{:s}/pids/3/setpoint', new_value)


def set_pid_params(mdrec, dev='dev30794', piezo_params=None, laser_params=None, piezo_aux=0, laser_aux=3, demodulator=1, 
                   piezo_out=0, laser_out=3, piezo_center=2.5, laser_range=0.1):
    """
    Configure PID controller parameters for both piezo and laser channels.
    
    Args:
        mdrec: Demodulation recorder instance
        dev (str): Device ID
        piezo_params (list): [P, I, D] parameters for piezo controller
        laser_params (list): [P, I, D] parameters for laser controller
        piezo_aux (int): Auxiliary output index for piezo
        laser_aux (int): Auxiliary output index for laser
        demodulator (int): Demodulator index
        piezo_out (int): Piezo output channel
        laser_out (int): Laser output channel
        piezo_center (float): Center voltage for piezo
        laser_range (float): Voltage range for laser
    """
    if piezo_params is None:
        piezo_params = default_piezo_parameters
    if laser_params is None:
        laser_params = default_laser_parametrs

    mdrec.lock_in.set('/{:s}/pids/0/p'.format(dev), piezo_params[0])
    mdrec.lock_in.set('/{:s}/pids/0/i'.format(dev), piezo_params[1])
    mdrec.lock_in.set('/{:s}/pids/3/p'.format(dev), laser_params[0])
    mdrec.lock_in.set('/{:s}/pids/3/i'.format(dev), laser_params[1])

    mdrec.lock_in.set('/{:s}/pids/{:d}/input'.format(dev, piezo_aux), 1)
    mdrec.lock_in.set('/{:s}/pids/{:d}/inputchannel'.format(dev, piezo_aux), demodulator-1)
    mdrec.lock_in.set('/{:s}/pids/{:d}/output'.format(dev, piezo_aux), 5)
    mdrec.lock_in.set('/{:s}/pids/{:d}/outputchannel'.format(dev, piezo_aux), piezo_out)
    mdrec.lock_in.set('/{:s}/pids/{:d}/center'.format(dev, piezo_aux), piezo_center)
    mdrec.lock_in.set('/{:s}/pids/{:d}/limitlower'.format(dev, piezo_aux), -piezo_center)
    mdrec.lock_in.set('/{:s}/pids/{:d}/limitupper'.format(dev, piezo_aux), piezo_center)

    mdrec.lock_in.set('/{:s}/pids/{:d}/input'.format(dev, laser_aux), 1)
    mdrec.lock_in.set('/{:s}/pids/{:d}/inputchannel'.format(dev, laser_aux), demodulator-1)
    mdrec.lock_in.set('/{:s}/pids/{:d}/output'.format(dev, laser_aux), 5)
    mdrec.lock_in.set('/{:s}/pids/{:d}/outputchannel'.format(dev, laser_aux), laser_out)
    mdrec.lock_in.set('/{:s}/pids/{:d}/center'.format(dev, laser_aux), 0)
    mdrec.lock_in.set('/{:s}/pids/{:d}/limitlower'.format(dev, laser_aux), -laser_range)
    mdrec.lock_in.set('/{:s}/pids/{:d}/limitupper'.format(dev, laser_aux), laser_range)