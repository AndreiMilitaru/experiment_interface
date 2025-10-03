"""
author: Andrei Militaru
organization: Institute of Science and Technology Austria (ISTA)
date: October 2025
Description: Utilities for calibrating the phase signal at the Mach Zehnder output. 
"""

import numpy as np
from scipy.optimize import curve_fit
from .mach_zehnder_lock import df2tc

detector_offset = 200e-3  # Volts

def drive_phase(mdrec, dev='dev30794', drive_demodulator=1, drive_oscillator=1, drive_freq=100, drive_amp=1, trace_duration=1, reset_pids=False):

    # Turn off the PID temporarily
    mdrec.lock_in.set('/{:s}/pids/0/enable'.format(dev), 0)
    mdrec.lock_in.set('/{:s}/pids/3/enable'.format(dev), 0)

    # Set the drive parameters
    mdrec.lock_in.set('/{:s}/oscs/{:d}/freq'.format(dev, drive_oscillator), drive_freq)
    mdrec.lock_in.set('/{:s}/demods/{:d}/oscselect'.format(dev, drive_demodulator), drive_oscillator)
    mdrec.lock_in.set('/{:s}/demods/{:d}/adcselect'.format(dev, drive_demodulator), 174)
    mdrec.lock_in.set('/{:s}/demods/{:d}/timeconstant'.format(dev, drive_demodulator), df2tc(drive_freq*100))

    # Activating the phase drive
    mdrec.lock_in.set('/{:s}/auxouts/0/offset'.format(dev), 2.5)
    mdrec.lock_in.set('/{:s}/auxouts/0/outputselect'.format(dev), 0)
    mdrec.lock_in.set('/{:s}/auxouts/0/preoffset'.format(dev), 0.)
    mdrec.lock_in.set('/{:s}/auxouts/0/scale'.format(dev), 1)

    # Collecting demodulated timetrace
    dat = mdrec.record_timtrace(T=trace_duration)

    # Turning off the phase drive
    mdrec.lock_in.set('/{:s}/auxouts/0/outputselect'.format(dev), -1)
    mdrec.lock_in.set('/{:s}/auxouts/0/offset'.format(dev), 2.5)

    # Resetting the PID if needed
    if reset_pids:
        mdrec.lock_in.set('/{:s}/pids/0/enable'.format(dev), 1)
        mdrec.lock_in.set('/{:s}/pids/3/enable'.format(dev), 1)

    return np.imag(dat['signal']['trace'])


def calibrate_range(mdrec, dev='dev30794', **kwargs):
    trace = drive_phase(mdrec, dev=dev, **kwargs)
    vmin, vmax = np.min(trace), np.max(trace)
    hist, bin_edges = np.histogram(trace, bins=200, density=True, range=(vmin, vmax))
    vmin, vmax = np.min(trace), np.max(trace)
    guess = [np.min(hist[1:-2])*(vmax-vmin)/2, vmin, vmax]
    par, cov = curve_fit(unlock_model, bins[1:-3], hist[1:-2], guess)
    return par, cov, hist, bin_edges


def evaluate_visibility(par):
    vmin = par[1]
    vmax = par[2]
    return (vmax - vmin) / (vmax + vmin - 2*detector_offset)


def evaluate_lock_precision(mdrec, dev='dev30794', duration=10, par):
    dat = mdrec.record_timtrace(T=duration)
    trace = np.imag(dat['signal']['trace'])
    hist, bin_edges = np.histogram(trace, bins=200, density=True, range=(par[1], par[2]))
    phi, fphi = convert(bin_edges[:-1], hist, par)
    fphi_max = np.max(fphi)
    mu_guess = phi[np.argmax(fphi)]
    sig2_guess = (mu_guess - phi(np.where(fphi > fphi_max/np.exp(-1/2))[0][0]))**2
    guess = [mu_guess, sig2_guess]
    par_lock, cov_lock = curve_fit(lock_model, phi, fphi, guess)
    return par_lock, cov_lock, hist, bin_edges


def V2phi(V, par):
    V0 = par[1]
    V1 = par[2]
    return np.arcsin( 2*(V-V0)/(V1-V0) - 1 ) + np.pi/2


def correction(V, par):
    V0 = par[1]
    V1 = par[2]
    #return (V1-V0)/2*np.sqrt((V-V0)*(V1-V))
    return np.sqrt(-(V-V0)**2 + (V-V0)*(V1-V0))


def convert(V, fV, par):
    print(len(V), len(fV))
    return V2phi(V, par), fV*correction(V, par)


def lock_model(x, mu, sig2):
    return 1/np.sqrt(2*np.pi*sig2) * np.exp(- (x-mu)**2/(2*sig2))


def unlock_model(x, A, x0, x1):
    return A/np.sqrt( (x-x0)*(x1-x) )
