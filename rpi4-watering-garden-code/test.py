import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

duration = ctrl.Consequent(np.arange(0, 180, 1), 'duration')

drtn = ['pendek', 'sedang', 'lama']
duration.automf(names=drtn)

duration['sedang'].view()