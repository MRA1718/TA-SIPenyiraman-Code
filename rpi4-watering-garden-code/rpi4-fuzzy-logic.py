import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

soil1 = ctrl.Antecedent(np.arange(0, 100, 1), 'soil1')
soil2 = ctrl.Antecedent(np.arange(0, 100, 1), 'soil2')
temperature = ctrl.Antecedent(np.arange(20, 45, 1), 'temperature')
humidity = ctrl.Antecedent(np.arange(0, 100, 1), 'humidity')
light = ctrl.Antecedent(np.arange(0, 1000, 1), 'light')
duration = ctrl.Consequent(np.arange(0, 180, 1), 'duration')

#soil1
soil1['kering'] = fuzz.trapmf(soil1.universe, [0, 0, 30, 45])
soil1['lembab'] = fuzz.trapmf(soil1.universe, [30, 50, 70, 85])
soil1['basah'] = fuzz.trapmf(soil1.universe, [70, 80, 100, 100])

#soil2
soil2['kering'] = fuzz.trapmf(soil2.universe, [0, 0, 30, 45])
soil2['lembab'] = fuzz.trapmf(soil2.universe, [30, 50, 70, 85])
soil2['basah'] = fuzz.trapmf(soil2.universe, [70, 80, 100, 100])

#temperature
temperature['dingin'] = fuzz.trapmf(temperature.universe, [20, 20, 22, 25])
temperature['hangat'] = fuzz.trapmf(temperature.universe, [23, 25, 32, 36])
temperature['panas'] = fuzz.trapmf(temperature.universe, [30, 35, 45, 45]) 

#humidity
humidity['kering'] = fuzz.trapmf(humidity.universe, [0, 0, 30, 40])
humidity['lembab'] = fuzz.trapmf(humidity.universe, [30, 40, 60, 80])
humidity['basah'] = fuzz.trapmf(humidity.universe, [70, 80, 100, 100])

#light
light['gelap'] = fuzz.trapmf(light.universe, [0, 0, 200, 400])
light['redup'] = fuzz.trapmf(light.universe, [200, 400, 600, 800])
light['terang'] = fuzz.trapmf(light.universe, [600, 800, 1000, 1000])

#duration
duration['pendek'] = fuzz.trapmf(duration.universe, [0, 0, 45, 75])
duration['sedang'] = fuzz.trapmf(duration.universe, [40, 75, 105, 135])
duration['lama'] = fuzz.trapmf(duration.universe, [105, 135, 180, 180])
# duration['pendek'] = fuzz.trimf(duration.universe, [0, 0, 60])
# duration['sedang'] = fuzz.trimf(duration.universe, [30, 90, 150])
# duration['lama'] = fuzz.trimf(duration.universe, [120, 180, 180])



# drtn = ['pendek', 'sedang', 'lama']
# duration.automf(names=drtn)

duration.view()
# soil2.view()

input()