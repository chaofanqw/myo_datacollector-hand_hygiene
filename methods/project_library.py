import ntplib
import time
import csv
import matplotlib.pyplot as plt
import os
import pandas


def get_time_offset():
    c = ntplib.NTPClient()
    response = c.request('au.pool.ntp.org', version=3)
    return response.tx_time, response.offset


def plot_result():
    result = pandas.read_csv('../data/data_diff.csv')
    # time_offset = list(result['TimeOffset'])
    plt.plot(result['Time'], result['TimeOffset'])
    plt.show()


def generate_result():
    times = 6 * 60 * 18
    time_diff = []
    f = open('../data/data_diff.csv', 'w')
    time_writer = csv.writer(f)
    time_writer.writerow(['Time', 'TimeOffset'])

    for each in range(0, times):
        try:
            time_diff.append([*get_time_offset()])
            time_writer.writerow(time_diff[-1])
            f.flush()
            print(each, time_diff[-1])
            time.sleep(10)
        except:
            continue

    f.close()


if __name__ == '__main__':
    if not os.path.exists('../data/data_diff.csv'):
        generate_result()
    else:
        plot_result()
