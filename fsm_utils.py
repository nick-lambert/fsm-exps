import numpy as np
import astropy.units as u
import time 

import magpyx
from magpyx.utils import ImageStream
import purepyindi
from purepyindi import INDIClient
import purepyindi2
from purepyindi2 import IndiClient

L = 12*u.mm # distance between FSM piezo actuators
B = L * np.cos(30*u.degree) # baseline distance of three piezos
max_stroke = 10*u.um
max_voltage = 100
D_per_V = max_stroke/max_voltage
# D_per_V = 0.05*u.um

def get_A(alpha, Z):
    return (Z + 2./3. * B * alpha).to(u.m)

def get_B(alpha, beta, Z):
    return (0.5 * L * beta + Z - 1./3. * B * alpha).to(u.m)

def get_C(alpha, beta, Z):
    return (Z - 1./3. * B * alpha - 1./2. * L * beta).to(u.m)

def get_fsm_volts(tip, tilt, dZ=5*u.um):
    tip = tip.to_value(u.radian)
    tilt = tilt.to_value(u.radian)

    dA = get_A(tip, dZ)
    dB = get_B(tip, tilt, dZ)
    dC = get_C(tip, tilt, dZ)
    print(f'Displacements: A = {dA:.2e}, {dB:.2e}, {dC:.2e}. ')

    dvA = (dA/D_per_V).decompose().value
    dvB = (dB/D_per_V).decompose().value
    dvC = (dC/D_per_V).decompose().value
    print(f'Delta Voltages: A = {dvA:.2f}, B = {dvB:.2f}, C = {dvC:.2f}. ')

    return np.array([[dvA, dvB, dvC]]).T

def set_fsm_mod_amp(amp, client, delay=0.25):
    client.wait_for_properties(['fsmModulator.amp'])
    client['fsmModulator.amp.target'] = amp
    time.sleep(delay)

def set_fsm_mod_rate(freq, client, delay=0.25):
    client.wait_for_properties(['fsmModulator.frequency'])
    client['fsmModulator.frequency.target'] = freq
    time.sleep(delay)

def start_fsm_mod(client, delay=0.25):
    client.wait_for_properties(['fsmModulator.trigger', 'fsmModulator.modulating'])
    client['fsmModulator.trigger.toggle'] = purepyindi.SwitchState.OFF
    time.sleep(delay)
    client['fsmModulator.modulating.toggle'] = purepyindi.SwitchState.ON
    time.sleep(delay)

def stop_fsm_mod(client, delay=0.25):
    client.wait_for_properties(['fsmModulator.trigger', 'fsmModulator.modulating', 'fsmModulator.zero'])
    client['fsmModulator.modulating.toggle'] = purepyindi.SwitchState.OFF
    time.sleep(delay)
    client['fsmModulator.trigger.toggle'] = purepyindi.SwitchState.ON
    time.sleep(delay)
    client['fsmModulator.zero.request'] = purepyindi.SwitchState.ON
