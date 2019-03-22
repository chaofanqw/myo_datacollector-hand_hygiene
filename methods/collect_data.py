# The MIT License (MIT)
#
# Copyright (c) 2017 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


"""
Before using this document to collect myo data,
please edit the myo-python library, at
*Event* class in *myo._ffi.py*

by adding:

  @property
  def device_point(self):
    return libmyo.libmyo_event_get_myo(self._handle)

"""

from matplotlib import pyplot as plt
from threading import Lock, Thread

import myo
import numpy as np
import sys
import datetime
import csv
import os


class DataCollector(myo.DeviceListener):
    """
    Collects EMG data in a queue with *n* maximum number of elements.
    """

    def __init__(self, n, device_start, device_end):
        self.n = n
        self.device_start = device_start
        self.device_end = device_end

        self.lock = Lock()
        self.data_queue = generate_data_queue(self.device_start, self.device_end)
        self.devices = {}
        self.participant = {}
        self.time = datetime.datetime.timestamp(datetime.datetime.now()) * 1000000

        self.installation = True

    def get_data(self, data_type, hand):
        with self.lock:
            if len(self.data_queue[data_type][hand]) <= self.n:
                return self.data_queue[data_type][hand]
            else:
                return self.data_queue[data_type][hand][-512:]

    # myo.DeviceListener

    def on_connected(self, event):
        event.device.stream_emg(True)

        with self.lock:
            self.devices[str(event.device_point)] = \
                str(devices.index(str(event.mac_address)) + 1)

    def on_emg(self, event):
        with self.lock:
            time_now = event.timestamp
            time_diff = time_now - self.time
            frame_number = int(time_diff // 40000)

            self.data_queue['emg'][self.devices[str(event.device_point)]] \
                .append((event.timestamp, event.emg, frame_number, time_now))

    def on_orientation(self, event):
        with self.lock:
            time_now = event.timestamp
            time_diff = time_now - self.time
            frame_number = int(time_diff // 40000)
            self.data_queue['orientation'][self.devices[str(event.device_point)]] \
                .append((event.timestamp, event.orientation, frame_number, time_now))
            self.data_queue['acceleration'][self.devices[str(event.device_point)]] \
                .append((event.timestamp, event.acceleration, frame_number, time_now))
            self.data_queue['gyroscope'][self.devices[str(event.device_point)]] \
                .append((event.timestamp, event.gyroscope, frame_number, time_now))

    def set_participant(self, participant_info):
        with self.lock:
            if self.participant is not None:
                if self.participant['participant_name'] != participant_info['participant_name']:
                    self.installation = True

            self.participant = participant_info

            if self.installation:
                self.participant['experiment_times'] = '0'
                self.dump_doc()

            self.participant = participant_info
            self.data_queue = generate_data_queue(self.device_start, self.device_end)
            self.time = datetime.datetime.timestamp(datetime.datetime.now()) * 1000000

    def dump_doc(self):
        data_path = '../data/'
        data_path_participant = data_path + 'person-' + self.participant['participant_name'] + '/'
        data_path_participant_record = data_path_participant + 'Experiment-' + self.participant['experiment_times'] + '/'

        demo = True if self.participant['video_type'] == 'With Demonstration' else False
        display_type = 'Poster' if 'Poster' in self.participant['video_type'] else 'Video'

        base_attributes = ['-MyoNum', 'Hand', 'TimeInMilliSec', 'ParticipantNum',
                           'WearingPos', 'RecordType', 'DisplayType', 'withDemon', 'numFrame', 'DataType']

        if not os.path.exists(data_path):
            os.mkdir(data_path)
        if not os.path.exists(data_path_participant):
            os.mkdir(data_path_participant)
        if not os.path.exists(data_path_participant_record):
            os.mkdir(data_path_participant_record)

        for signal in self.data_queue:
            if signal == 'emg':
                attributes = base_attributes + ['d' + str(i) for i in range(1, 9)]
            elif signal == 'orientation':
                attributes = base_attributes + ['roll', 'pitch', 'yaw', 'magnitude']
            else:
                attributes = base_attributes + ['x', 'y', 'z']

            for hand in self.data_queue[signal]:
                arm_position = self.participant['position'].split(' ')[int(hand) - 1]
                arm = arm_position.split('-')[0]
                position = arm_position.split('-')[1]

                csv_doc = open(data_path_participant_record + signal + '_' + arm + '_' + position + '.csv', 'w')
                csv_writer = csv.writer(csv_doc)
                csv_writer.writerow(attributes)

                for row in self.data_queue[signal][hand]:
                    record_base = ['Myo-' + hand, arm, row[3],
                                   self.participant['participant_name'], position,
                                   'Record', display_type, demo, row[2]]

                    if signal == 'emg':
                        csv_writer.writerow(record_base + ['EmgData'] + row[1])
                    elif signal == 'orientation':
                        csv_writer.writerow(record_base + ['OriData'] + list(row[1]))
                    elif signal == 'gyroscope':
                        csv_writer.writerow(record_base + ['GyroData'] + list(row[1]))
                    elif signal == 'acceleration':
                        csv_writer.writerow(record_base + ['AcceleData'] + list(row[1]))

                csv_doc.close()


class Plot(object):
    def __init__(self, listener):
        self.n = listener.n
        self.listener = listener
        self.fig = plt.figure()

        self.start = listener.device_start
        self.end = listener.device_end
        self.device_num = self.end - self.start + 1

        self.axes = [self.fig.add_subplot(8, self.device_num, i) for i in range(1, self.device_num * 8 + 1)]
        [(ax.set_ylim([-100, 100]), ax.set_xticks([]),
          ax.set_yticks([])) for ax in self.axes]

        self.graphs = [ax.plot(np.arange(self.n), np.zeros(self.n))[0] for ax in self.axes]
        plt.ion()

    def update_plot(self):
        emg_data = [self.listener.get_data('emg', str(device))
                    for device in range(self.start, self.end + 1)]

        [(self.set_plot(emg_data[device], self.graphs[device::self.device_num]))
         for device in range(0, self.device_num)]

        plt.draw()

    def set_plot(self, emg_data, graphs):
        emg_data = np.array([x[1] for x in emg_data]).T

        for g, data in zip(graphs, emg_data):
            if len(data) < self.n:
                # Fill the left side with zeroes.
                data = np.concatenate([np.zeros(self.n - len(data)), data])
            g.set_ydata(data)

    def main(self):
        while True:
            self.update_plot()
            plt.pause(1.0 / 50)

    def data_plot(self, pipe):
        while True:
            if pipe.poll():
                info = pipe.recv()
                if info['status'] == 'start':
                    self.listener.set_participant(info)
                elif info['status'] == 'end':
                    self.listener.dump_doc()

            self.update_plot()
            plt.pause(1.0 / 50)


def generate_data_queue(num_start, num_end):
    result = {}
    for signal in signals:
        result[signal] = {}
        for device in range(num_start - 1, num_end):
            result[signal][str(device + 1)] = []

    return result


def main():
    if sys.platform.startswith('win'):
        path = '../myo_sdk/sdk_windows'
        device_start, device_end = 1, 2
    elif sys.platform.startswith('darwin'):
        path = './myo_sdk/sdk_macos'
        device_start, device_end = 3, 4

    myo.init(sdk_path=path)
    hub = myo.Hub()
    listener = DataCollector(512, device_start, device_end)
    with hub.run_in_background(listener.on_event):
        Plot(listener).main()


signals = ['emg', 'orientation', 'gyroscope', 'acceleration']
devices = ['9B:FA:53:BC:C7:ED', '27:DE:FB:9B:2F:FF', 'CD:77:5E:B2:99:D2', '36:B5:0C:6A:BB:D6']

if __name__ == '__main__':
    main()
