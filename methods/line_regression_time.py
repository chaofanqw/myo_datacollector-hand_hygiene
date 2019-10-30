from sklearn.linear_model import TheilSenRegressor
import pandas as pd
import methods.project_library as time_shift
import numpy
from matplotlib import pyplot as plt
import numpy as np
import datetime

documents = ['../data/time_diff/data_diff_24hour.csv', '../data/time_diff/data_diff_24hour_2.csv',
             '../data/time_diff/data_diff_24hour_3.csv']

for document in range(0, len(documents)):
    plt.subplot(3, 1, document + 1)
    estimators = TheilSenRegressor()

    result = pd.read_csv(documents[document]).iloc[:5001]
    timestamp = numpy.array(result['Time']).reshape(-1, 1)
    time_offset = result['TimeOffset']
    time_result = [datetime.datetime.fromtimestamp(each).strftime('%H:%M') for each in list(result['Time'])]

    estimators.fit(timestamp, time_offset)

    plt.xticks(range(0, len(time_result), 1000), [time_result[each] for each in range(0, len(time_result), 1000)])
    plt.yticks(np.arange(min(time_offset)//1.0, max(time_offset)//1.0 + 1, 0.25))
    plt.plot(time_offset, label='NTP Records')
    plt.plot(estimators.predict(timestamp), label='Regression Result')

    time_predicted = time_shift.get_time_offset()
    result = estimators.predict(numpy.array(time_predicted[0]).reshape(-1, 1))
    print('Prediction(Predicted, NTPlib):', result, time_predicted[1])
    print('Daily time shifting', estimators.coef_[0] * 60 * 60 * 24)
    plt.legend()

plt.show()
