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


class DataCollector(myo.DeviceListener):
    """
    Collects EMG data in a queue with *n* maximum number of elements.
    """

    def __init__(self, n):
        self.n = n
        self.lock = Lock()
        self.data_queue = {'emg': {'left': [], 'right': []},
                           'orientation': {'left': [], 'right': []},
                           'gyroscope': {'left': [], 'right': []},
                           'acceleration': {'left': [], 'right': []}}
        self.devices = {}

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
            if str(event.mac_address) == '9B:FA:53:BC:C7:ED':
                self.devices[str(event.device_point)] = 'left'
            elif str(event.mac_address) == '27:DE:FB:9B:2F:FF':
                self.devices[str(event.device_point)] = 'right'

    def on_emg(self, event):
        with self.lock:
            self.data_queue['emg'][self.devices[str(event.device_point)]] \
                .append((event.timestamp, event.emg))

    def on_orientation(self, event):
        with self.lock:
            self.data_queue['orientation'][self.devices[str(event.device_point)]] \
                .append((event.timestamp, event.orientation))
            self.data_queue['acceleration'][self.devices[str(event.device_point)]] \
                .append((event.timestamp, event.acceleration))
            self.data_queue['gyroscope'][self.devices[str(event.device_point)]] \
                .append((event.timestamp, event.gyroscope))


class Plot(object):

    def __init__(self, listener):
        self.n = listener.n
        self.listener = listener
        self.fig = plt.figure()
        self.axes = [self.fig.add_subplot(8, 2, i) for i in range(1, 17)]
        [(ax.set_ylim([-100, 100]), ax.set_xticks([]),
          ax.set_yticks([])) for ax in self.axes]

        self.graphs = [ax.plot(np.arange(self.n), np.zeros(self.n))[0] for ax in self.axes]
        plt.ion()

    def update_plot(self):
        emg_data_left = self.listener.get_data('emg', 'left')
        emg_data_right = self.listener.get_data('emg', 'right')

        self.set_plot(emg_data_left, self.graphs[0::2])
        self.set_plot(emg_data_right, self.graphs[1::2])

        # plt.set_title()

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


def main(path):
    myo.init(sdk_path=path)
    hub = myo.Hub()
    listener = DataCollector(512)
    with hub.run_in_background(listener.on_event):
        Plot(listener).main()


if __name__ == '__main__':
    main('../myo_sdk/sdk_windows')
