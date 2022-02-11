'''
Analysis of responses to current pulses.
'''
from __future__ import print_function
from pylab import *
from clampy import *
from clampy.setup.units import *
from clampy.analysis.spike_analysis import lowpass
from clampy.data_management import print_and_log

__all__ = ['do_analysis']

def do_analysis(path, filtering = 1*ms, display=True):
    print('* Analysis *')

    # *** Loading ***
    # Parameters
    info = load_info(path+'/protocol.yaml')
    dt, ntrials = info['dt'], info['ntrials']
    start, end = info['start'], info['end']
    amplitudes = array(info['amplitudes'])

    # Log file
    log_file = path+'/log.txt'

    # Load pulse experiment
    signals = load_dataset(path+'/electrophysiology/data')
    V1, V2, Ic, t = signals['V1'], signals['V2'], signals['Ic2'], signals['t']

    # *** Analysis ***
    # Offset between the two headstages
    delta_V = mean(V2[:,:int(start/dt)]) - mean(V1[:,:int(start/dt)])
    print_and_log(log_file,"Offset between the two traces = {} mV".format(delta_V/mV))

    # Passive properties from the smallest negative pulse
    neg_amplitudes = (amplitudes<0).nonzero()[0]
    if neg_amplitudes != []:
        i = neg_amplitudes[argmax(amplitudes[neg_amplitudes])]
        ampli = amplitudes[i]
        v1_0 = mean(V1[i,:int(start / dt)])
        v2_0 = mean(V2[i,:int(start / dt)])
        delta_v1 = mean(V1[i,int((end-50*ms)/ dt):int((end) / dt)]) - v1_0
        delta_v2 = mean(V2[i,int((end-50*ms)/ dt):int((end) / dt)]) - v2_0
        R = delta_v1/ampli
        Re = (delta_v2-delta_v1)/ampli
        print_and_log(log_file,'Rm = {} MOhm'.format(R/1e6))
        print_and_log(log_file,'Re = {} MOhm'.format(Re/1e6))

    # Calculate initial potential before the pulse
    Vstart=mean(V1[:,:int(start / dt)], axis=1)

    # *** Plotting ***
    figure()
    plot(Vstart/mV,'k')
    xlabel('Trial')
    ylabel('V0 (mV)')
    title("Initial potential")
    savefig(path+'/Initial potential.pdf')

    figure()
    for Vi,V2i,Ici in zip(V1,V2,Ic):
        plot(t/ms, lowpass(array(Vi) / mV, filtering, dt=dt), 'k', linewidth=.5)
        plot(t / ms, lowpass(array(V2i) / mV, filtering, dt=dt), 'r', linewidth=.5)
    ylim(-100, 100)
    xlabel('Time (ms)')
    ylabel('Vm (mV)')
    title('Responses to pulses')
    savefig(path+'/Responses to pulses.pdf')

    # Late current (at the end of the pulse)
    V_late = array([Vi[int((end - 1 * ms) / dt)] for Vi in V1])
    # Sort
    ind = argsort(amplitudes)
    figure()
    plot(V_late[ind] / mV, amplitudes[ind] / nA, 'k')
    ylabel('I (nA)')
    xlabel('V (mV)')
    title('Late current')
    savefig(path+'/Late current.pdf')

    if display:
        show()


if __name__ == '__main__':
    do_analysis('.')
