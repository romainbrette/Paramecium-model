'''
Initializes for model running mode.
See the documentation of Clampy for initialization files for amplifiers.
'''
from brian2 import *
from clampy.brianmodels import *

dt = 0.1*ms
board = RC_and_electrode(Ce = 3*pF)
board.set_aliases(Ic1='Ic', Ic2='Ic', I_TEVC='I', V1='V')
