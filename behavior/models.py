'''
Full model
'''
from brian2 import *
from brian2.units.constants import faraday_constant,gas_constant
from scipy.special import exprel
from file_management import *
import csv
from os.path import split

__all__ = ['paramecium_constants', 'paramecium_equations']

## Build the table of Paramecium constants
paramecium_table = {}
rows = []
units = {}
with open(split(__file__)[0]+'/../models/full_models/ciliated.csv') as f:
    reader = csv.DictReader(f, delimiter=';')
    for i, row in enumerate(reader):
        if i == 0: # units
            units = dict(row)
        else:
            constants = dict(row)
            for key, value in row.items():
                try:
                    constants[key] = float(value)*eval(units[key])
                except: # name
                    if key != '':
                        date = value[:-5]
            paramecium_table[date] = constants
            paramecium_table[i-1] = constants

def paramecium_constants(name = '2020-10-28 17.46.05'):
    if name is None:
        name = '2020-10-28 17.46.05'
    constants = paramecium_table[name]

    constants.update(dict(K_electromotor = 1.4e-6*molar,
        F=faraday_constant,
        R=gas_constant,
        DV=gas_constant * (273 + 20.) * kelvin / faraday_constant,  # 20 °C

        v_plus = 0.5*mm/second,
        v_minus = -0.5*mm/second,
        theta_min = 13*pi/180,
        theta_max = 90*pi/180,
        omega_min = 2*pi/second,
        omega_max = 8*pi/second,
        n_electromotor_coupling = 2
    ))

    constants['g_IK']*= 0.0252487776994807 # from siemens to amp

    return constants

def paramecium_equations(name=None):
    return Equations('''
            IL = gL*(EL-v) : amp
            IV_K = (EK-v)/DV : 1
            IV_Ca = 1/exprel(2*v/DV) : 1
            
            ## IK (rectifier)
            IK = g_IK * n_IK**2 * IV_K : amp
            ninf_IK = 1/(1+exp((V_IK-v)/k_IK)) : 1
            dn_IK / dt = (ninf_IK - n_IK)/tau_IK: 1
            tau_IK = a_IK + b_IK/(cosh((v-V_IK)/(2*k_IK))) : second
            
            ## IKir (inward rectifier)
            IKir = 0*amp : amp
            #IKir = g_IKir * n_IKir**2 * IV_K : amp
            #ninf_IKir = 1/(1+exp((v-V_IKir)/k_IKir)) : 1
            #dn_IKir / dt = (ninf_IKir - n_IKir)/tau_IKir: 1
            
            ### ICa_cilia (depolarization-activated)
            ICa_cilia = gCa_cilia*m_Ca_cilia**2*h_Ca_cilia*IV_Ca : amp
            dm_Ca_cilia/dt = (minf_Ca_cilia-m_Ca_cilia)/taum_Ca_cilia : 1
            minf_Ca_cilia = 1/(1+exp((VCa_cilia-v)/kCa_cilia)) : 1
            h_Ca_cilia = 1/(1+exp(nCaM_Ca_cilia*(pCa-pKCa))) : 1
            
            ### IK(Ca)
            IKCa_cilia = gKCa_cilia / (1+ exp(-nCaM_KCa_cilia*(pCa-pKKCa)))* IV_K : amp # gKCa is the amplitude at 10 uM
            
            #### Calcium dynamics ####
            dpCa/dt = ICa_cilia/(2*F*Cai0_cilia*v_cilia)*exp(-pCa) + alpha_cilia*(exp(-pCa)-1)- Jpump_cilia : 1
            Jpump_cilia = Jpumpmax_cilia / (1+exp(pCa)) : 1/second
            Cai_cilia = Cai0_cilia*exp(pCa) : mM
            
            ### Electromotor coupling
            velocity = -v_plus + 2*v_plus/(1+(Cai_cilia/K_electromotor)**2) : meter/second (constant over dt)
            theta = theta_min + 2*(theta_max-theta_min)/((K_electromotor/Cai_cilia)**2 + (Cai_cilia/K_electromotor)**2) : 1 (constant over dt)
            omega = omega_min + 2*(omega_max-omega_min)/((K_electromotor/Cai_cilia)**2 + (Cai_cilia/K_electromotor)**2) : 1/second (constant over dt)
            ''', **paramecium_constants(name))

## Responses
if __name__ == '__main__':
    cell = None
    C = paramecium_constants(cell)['C']
    print(C)

    N = 10
    t1 = 300*ms
    t2 = 302*ms

    eqs = paramecium_equations(cell) + Equations('''
    dv/dt = (IL+ICa_cilia+IK+IKCa_cilia+I)/C : volt
    I = I0*(int(t>t1)*int(t<t2)) : amp
    I0 : amp (constant)
    ''')

    neuron = NeuronGroup(N, eqs)
    neuron.v = paramecium_constants(cell)['EL']
    neuron.I0 = linspace(0, 4, N)*nA

    M = StateMonitor(neuron, ('v', 'Cai_cilia', 'velocity', 'theta', 'omega', 'ICa_cilia', 'IK', 'IKCa_cilia'), record=True)

    run(700*ms)

    subplot(511)
    for i in range(N):
        plot(M.t/ms, M.v[i]/mV)
    ylabel('v')

    subplot(512)
    for i in range(N):
        semilogy(M.t/ms, M.Cai_cilia[i]/molar)
    ylabel(r'[Ca$^2+$]')

    subplot(513)
    for i in range(N):
        plot(M.t/ms, M.velocity[i]/(mm/second))
    plot(M.t / ms, 0*M.t,'--k')
    ylabel('v')

    subplot(514)
    for i in range(N):
        plot(M.t/ms, M.theta[i]*180/np.pi)
    ylabel(r'$\theta$')

    subplot(515)
    for i in range(N):
        plot(M.t/ms, M.omega[i]/(2*np.pi)*second)
    ylabel(r'$\omega$')

    # figure()
    # subplot(311)
    # for i in range(N):
    #     plot(M.t/ms, M.ICa_cilia[i]/nA)
    # ylabel('ICa')
    # subplot(312)
    # for i in range(N):
    #     plot(M.t/ms, M.IKCa_cilia[i]/nA)
    # ylabel('IKCa')
    # subplot(313)
    # for i in range(N):
    #     plot(M.t/ms, M.IK[i]/nA)
    # ylabel('IK')

    show()
