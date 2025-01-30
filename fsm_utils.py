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

def get_fsm_volts(tip, tilt, dZ=5*u.um, verbose=False):
    tip = tip.to_value(u.radian)/2
    tilt = tilt.to_value(u.radian)/2

    dA = get_A(tip, dZ)
    dB = get_B(tip, tilt, dZ)
    dC = get_C(tip, tilt, dZ)
    if verbose: print(f'Displacements: A = {dA:.2e}, {dB:.2e}, {dC:.2e}. ')

    dvA = (dA/D_per_V).decompose().value
    dvB = (dB/D_per_V).decompose().value
    dvC = (dC/D_per_V).decompose().value
    if verbose: print(f'Delta Voltages: A = {dvA:.2f}, B = {dvB:.2f}, C = {dvC:.2f}. ')

    return np.array([[dvA, dvB, dvC]]).T

def set_fsm_mod_amp(amp, client, process_name='fsmModulator', delay=0.25):
    client.wait_for_properties([f'{process_name}.amp'])
    client[f'{process_name}.amp.target'] = amp
    time.sleep(delay)

def set_fsm_mod_rate(freq, client, process_name='fsmModulator', delay=0.25):
    client.wait_for_properties([f'{process_name}.frequency'])
    client[f'{process_name}.frequency.target'] = freq
    time.sleep(delay)

def start_fsm_mod(client, process_name='fsmModulator', delay=0.25):
    client.wait_for_properties([f'{process_name}.trigger', f'{process_name}.modulating'])
    client[f'{process_name}.trigger.toggle'] = purepyindi.SwitchState.OFF
    time.sleep(delay)
    client[f'{process_name}.modulating.toggle'] = purepyindi.SwitchState.ON
    time.sleep(delay)

def stop_fsm_mod(client, process_name='fsmModulator', delay=0.25):
    client.wait_for_properties([f'{process_name}.trigger', f'{process_name}.modulating', f'{process_name}.zero'])
    client[f'{process_name}.modulating.toggle'] = purepyindi.SwitchState.OFF
    time.sleep(delay)
    client[f'{process_name}.trigger.toggle'] = purepyindi.SwitchState.ON
    time.sleep(delay)
    client[f'{process_name}.zero.request'] = purepyindi.SwitchState.ON
    time.sleep(delay)

def toggle_telem_campupil(on, client):
    client.wait_for_properties(['telem_campupil.writing'])
    if on:
        client[f'telem_campupil.writing.toggle'] = purepyindi.SwitchState.ON
    else:
        client[f'telem_campupil.writing.toggle'] = purepyindi.SwitchState.OFF

def toggle_telem_fsm(on, client):
    client.wait_for_properties(['telem_fsm.writing'])
    if on:
        client[f'telem_fsm.writing.toggle'] = purepyindi.SwitchState.ON
    else:
        client[f'telem_fsm.writing.toggle'] = purepyindi.SwitchState.OFF

import shutil
import os
import subprocess

def delete_all_data(dir_path):
    directory = str(dir_path)
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def move_files(source_path, target_path):
    file_names = os.listdir(str(source_path))
    for fname in file_names:
        # shutil.move(os.path.join(source_dir, file_name), target_dir)
        src = str(source_path/fname)
        dest = str(target_path)
        subprocess.run(['mv', src, dest], check=True)

