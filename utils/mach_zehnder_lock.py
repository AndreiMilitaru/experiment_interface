"""
author: Andrei Militaru
organization: Institute of Science and Technology Austria (ISTA)
date: October 2025
Description: Utilities for locking a Mach-Zehnder interferometer using Zurich Instruments devices.
I will be adding utilities as time passes based on what we need.
"""

import numpy as np


def df2tc(freq):
    return 1/(2*np.pi*freq)


def set_demodulators(mdrec, dev='dev30794', oscillator=0, demodulator=1, order=1, rate=53.57e3, bandwidth=20e3):
    mdrec.lock_in.set('/{:s}/oscs/{:d}/freq'.format(dev, oscillator), 0.)
    mdrec.lock_in.set('/{:s}/demods/{:d}/oscselect'.format(dev, demodulator), oscillator)
    mdrec.lock_in.set('/{:s}/demods/{:d}/adcselect'.format(dev, demodulator), 0)
    mdrec.lock_in.set('/{:s}/demods/{:d}/order'.format(dev, demodulator), order)
    mdrec.lock_in.set('/{:s}/demods/{:d}/timeconstant'.format(dev, demodulator), df2tc(bandwidth))
    mdrec.lock_in.set('/{:s}/demods/{:d}/rate'.format(dev, demodulator), rate)
    mdrec.lock_in.set('/{:s}/demods/{:d}/enable'.format(dev, demodulator), 1)
    mdrec.set_demod_list({'signal': (dev, 0)})


def set_aux_limits(mdrec, dev='dev30794', aux_lim=None, laser_lim=None):
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