from sklearn.linear_model import TheilSenRegressor
import pandas as pd
import methods.project_library as time_shift
import numpy
from matplotlib import pyplot as plt
import datetime

estimators = TheilSenRegressor()

result = pd.read_csv('../data/time_diff/data_diff.csv')
timestamp = numpy.array(result['Time']).reshape(-1, 1)
time_offset = result['TimeOffset']
time_result = [datetime.datetime.fromtimestamp(each).strftime('%H:%M') for each in list(result['Time'])]

estimators.fit(timestamp, time_offset)

plt.xticks(range(0, len(time_result), 1000), [time_result[each] for each in range(0, len(time_result), 1000)])
plt.plot(time_offset)
plt.plot(estimators.predict(timestamp))

time_predicted = time_shift.get_time_offset()
result = estimators.predict(numpy.array(time_predicted[0]).reshape(-1, 1))
print('Prediction(Predicted, NTPlib):', result, time_predicted[1])
print('Daily time shifting', estimators.coef_[0] * 60 * 60 * 24)

plt.show()

