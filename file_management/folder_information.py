'''
Information about cell folders

This is only useful for data with old formats, except cell_orientation.
'''
import os
import re
import datetime
from clampy import *
import yaml
import numpy as np

__all__ = ['read_lab_notes', 'is_PIV', 'protocol', 'protocols', 'stimulus_time', 'protocol_description',
           'recording_date', 'cell_orientation']

def cell_orientation(folder):
    '''
    Returns cell orientation (angle), modulo pi (front/rear not distinguished).
    '''
    if os.path.exists(os.path.join(folder,'manual_measurement.yaml')):
        filename = os.path.join(folder,'manual_measurement.yaml')
    elif os.path.exists(os.path.join(folder,'morphology.yaml')):
        filename = os.path.join(folder,'morphology.yaml')
    else:
        return None

    with open(filename, 'r') as fp:
        d = yaml.safe_load(fp)
    x1, y1 = d['anterior']
    x2, y2 = d['posterior']
    return -np.arctan2(y2-y1,x2-x1)

def stimulus_time(folder):
    '''
    Returns stimulus start and end times from the protocol folder (no units).
    '''
    d = protocol_description(folder)
    if 'pre_stimulus' in d:
        t_start = d['pre_stimulus']
    elif 'pulse_start' in d:
        t_start = d['pulse_start']
    if 'stimulus_duration' in d:
        duration = d['stimulus_duration']
    elif 'pulse_duration' in d:
        duration = d['pulse_duration']
    t_end = t_start + duration
    return t_start, t_end

def protocol_description(folder):
    '''
    Returns protocol description (dictionary) from the protocol folder.
    '''
    # Look for yaml file
    name = None

    for f in os.scandir(folder):
        if ((f.path[-5:]=='.yaml') and (f.path[-23:]!='manual_measurement.yaml')) or (f.path[-5:]=='.info'):
            name = f.path
            break
    if name is not None:
        info = load_info(name)
        return info
    else:
        return None

    # for f in os.scandir(folder):
    #     if f.path[-14:]=='_experiment.py':
    #         name = f.path[:-14]
    #         break
    # if name is None:
    #     return {}
    # path = os.path.join(folder,name)
    #
    # try:
    #     try:
    #         info = load_info(path+'.yaml')
    #     except FileNotFoundError:
    #         info = load_info(path+'.info')
    # except:
    #     info = {}
    # return info

def recording_date(folder):
    '''
    Returns the recording date from the folder name.
    '''
    _, filename = os.path.split(folder)
    try:
        groups = re.search(r'(\d+)\.(\d+)\.(\d+) (\d+)\.(\d+)\.(\d+)',filename).groups()
        day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
        if day>2000: # inverted
            day, year = year, day
        hour, minute, second = int(groups[3]), int(groups[4]), int(groups[5])
        return datetime.datetime(year=year, month=month, day=day,hour=hour, minute=minute, second=second)
    except:
        # Look at protocol dates
        dates = []
        for f in os.scandir(folder):
            if f.is_dir():
                date = recording_date(f.path)
                if date is not None:
                    dates.append(date)
        if len(dates)>0:
            return min(dates)
        else:
            return None

def read_lab_notes(folder):
    '''
    Reads lab notes in a subfolder and extract information.
    '''

    info = {}

    # Extract date and time # !! this is the cell date, not the protocol date
    date = recording_date(folder)
    info['date'] = date
    if date is not None:
        start_time = datetime.time(hour=date.hour, minute=date.minute, second=date.second)
        start_date = datetime.date(year=date.year, month=date.month, day=date.day)

    # Extract keywords from folder name
    keywords = ['example','pawn','pantophobiac','deciliated','calcium','PIV',
                'iron','silica','polystyrene','thick wall','thin wall','colchicine','VC','nickel','pressure']
    #_, filename = os.path.split(folder)
    for keyword in keywords:
        info[keyword] = (re.search(keyword, folder, flags=re.IGNORECASE) is not None)

    # Default solution
    info['extra KCl'] = 4.
    info['extra CaCl2'] = 1.

    # Look for a folder with lab notes
    # Either directly in the folder
    filename = None
    if os.path.exists(os.path.join(folder,"lab_notes.txt")):
        filename = os.path.join(folder,"lab_notes.txt")
    else:
        # Or in a subfolder
        for f in os.scandir(folder):
            if os.path.isdir(f) and os.path.exists(os.path.join(f.path,"lab_notes.txt")):
                filename = os.path.join(f.path,"lab_notes.txt")
                break

    if filename is None:
        return info

    with open(filename) as f:
        lab_notes = f.read()

    # Add folder name to the text

    # Extract information
    for keyword in keywords:
        if re.search(r'\b'+keyword+r'\b', lab_notes, flags=re.IGNORECASE):
            info[keyword] = True

    if info['example']: # The document was not filled
        return info

    # Agar bridge
    info['agar bridge'] = re.search(r'^Agar bridge', lab_notes, flags=re.IGNORECASE+re.M) is not None # default is no agar bridge

    # Intra solution
    result = re.search(r'^KCl ([\d\.]+)\s*M',lab_notes, flags=re.IGNORECASE+re.M)
    if result is None:
        info['intra KCl'] = 1 # Default 1 M
    else:
        info['intra KCl'] = float(result.group(1))

    # Extra solution
    # KCl
    result = re.search(r'(Solution|soln):.*?([\d\.]+)\s*mM KCl',lab_notes, flags=re.IGNORECASE+re.M)
    if result is None:
        info['extra KCl'] = 4. # Default  4 mM
    else:
        info['extra KCl'] = float(result.group(2))

    # CaCl2
    result = re.search(r'Solution:.*?([\d\.]+)\s*mM CaCl2',lab_notes, flags=re.IGNORECASE+re.M)
    if result is None:
        info['extra CaCl2'] = 1 # Default  1 mM
    else:
        info['extra CaCl2'] = float(result.group(1))

    # Culture date
    try:
        groups = re.search(r'culture.*?(\d+)/(\d+)/(\d+)',lab_notes,flags=re.IGNORECASE).groups()
        day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
        if year<100:
            year+=2000
        culture_date = datetime.date(day=day,month=month,year=year)
        info['culture'] = culture_date
        info['culture days'] = (start_date-culture_date).days # number of days since culture
    except:
        info['culture'] = None
        info['culture days'] = None

    # Equilibration time
    try:
        groups = re.search(r'(adaptation|cleaning).*?(\d+):(\d+)',lab_notes, flags=re.IGNORECASE+re.M).groups()
        hour, minute = int(groups[1]), int(groups[2])
        equilibration_start = 60*hour+minute
        info['equilibration'] = datetime.time(hour=hour, minute=minute)
        info['equilibration time'] = (60*start_time.hour+start_time.minute)-equilibration_start # in minutes
    except:
        info['equilibration'] = None
        info['equilibration time'] = None

    return info

def protocol(folder):
    '''
    Returns protocol type for the folder.
    '''
    name = os.path.split(folder)[1]
    if (('current_pulses' in name) or ('Current pulses' in name)):
        # Open info file
        try:
            info = load_info(folder + '/pulses.yaml')
            ntrials = info['ntrials']
            stimulus_duration, Imax, Imin = info['stimulus_duration'], info['I_max'], info['I_min']
        except FileNotFoundError:  # old version?
            info = load_info(folder + '/current_pulses.info')
            ntrials = info['ntrials']
            stimulus_duration, Imax, Imin = info['pulse_duration'], info['amplitude'], -info['amplitude']
        if ntrials >= 10: # otherwise fail
            if stimulus_duration<.03:
                return "short pulses"
            elif (Imin<-2e-9) and (Imax>2e-9):
                return "normal pulses"
            elif (Imin>-1e-9) and (Imax<1e-9):
                return "weak pulses"
            elif (Imax>10e-9):
                return "strong pulses"
    elif 'merged_pulses' in name:
        return 'merged pulses'
    elif ('random_current' in name):
        try:
            info = load_info(folder + '/random_current.yaml')
            Imax, Imin = info['I_max'], info['I_min']
        except FileNotFoundError:  # old version?
            return "" # We ignore
        if Imin<0.:
            return "random current"
        else:
            return "positive random current"
    elif ('random_pulses' in name):
        return "random pulses" # in some cases, there is a seed (repeated identical trials)
    elif ('long_pulses' in name):
        return "long pulses"

    return ""

def protocols(folder):
    '''
    Returns list of protocols in the folder
    '''
    results = [protocol(f.path) for f in os.scandir(folder) if os.path.isdir(f)]
    return [x for x in results if len(x)>0]

def is_PIV(folder):
    '''
    True if there is PIV data
    '''
    # Look into all folders to check if there is a PIV folder
    PIV = False
    for root, dirs, files in os.walk(folder):
        for dir in dirs:
            if dir[-4:]=='_PIV':
                PIV = True
                break
    return PIV

if __name__ == '__main__':
    folder = '/Volumes/Public/Paramecium/Electrophysiology/Session July-December 2020/5.11.2020 16.55.7 Cell_VC'
    print(read_lab_notes(folder))
