from sklearn.linear_model import TheilSenRegressor
import pandas as pd
import methods.project_library as time_shift
import numpy
from matplotlib import pyplot as plt

estimators = TheilSenRegressor()

result = pd.read_csv('../data/data_diff.csv')
timestamp = numpy.array(result['Time']).reshape(-1, 1)
time_offset = result['TimeOffset']

estimators.fit(timestamp, time_offset)
plt.plot(result['Time'], estimators.predict(timestamp))
plt.plot(result['Time'], time_offset)
plt.show()

time_predicted = time_shift.get_time_offset()
result = estimators.predict(numpy.array(time_predicted[0]).reshape(-1, 1))
print(result, time_predicted[1])