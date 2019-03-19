import ntplib
import time
import datetime
import csv


def get_time_offset():
    c = ntplib.NTPClient()
    response = c.request('au.pool.ntp.org', version=3)
    return response.tx_timestamp, response.offset


if __name__ == '__main__':
    times = 180
    time_diff = []

    for each in range(0, times):
        time_diff.append([*get_time_offset()])
        print(time_diff[-1])
        time.sleep(10)

    f = open('../data/data_diff.csv', 'w')
    time_writer = csv.writer(f)
    time_writer.writerow(['Time', 'TimeOffset'])

    for each in range(0, times):
        time_writer.writerow(time_diff[each])

    f.close()
