import sys
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication, QComboBox, \
    QLineEdit, QVBoxLayout, QMessageBox, QHBoxLayout, \
    QLabel, QPushButton
from PyQt5.QtCore import Qt
import methods.vlc_player as vlc_player
import methods.poster as poster
import methods.collect_data as collect_data
import methods.project_library as project_library
import myo
from multiprocessing import Process, Pipe
import socket
import sched
import time
import datetime
import json


"""
In Windows, please install vlc(x64) from https://www.videolan.org/vlc/download-windows.html ,
and set the environment path: PYTHON_VLC_MODULE_PATH: C:\Program Files\VideoLAN\VLC or other installed path;

In MacOS, it will be necessary install vlc by homebrew, with
brew cask install vlc
"""


class IPCollector(QWidget):

    def __init__(self):
        super().__init__()

        self.input_width = 300
        self.v_layout = QVBoxLayout()
        self.ip_address = QLineEdit()
        self.ip_port = QLineEdit()
        self.connection_btn = QPushButton('Connect')
        self.connection_btn.clicked.connect(self.connection)

        self.init_ui()

    def init_ui(self):
        ip_box = QHBoxLayout()
        ip_box.addWidget(QLabel('IP Address:'))
        self.ip_address.setFixedWidth(self.input_width)
        ip_box.addWidget(self.ip_address, alignment=Qt.AlignHCenter)
        self.v_layout.addLayout(ip_box)

        port_box = QHBoxLayout()
        port_box.addWidget(QLabel('Port:'))
        self.ip_port.setFixedWidth(self.input_width)
        port_box.addWidget(self.ip_port, alignment=Qt.AlignHCenter)
        self.v_layout.addLayout(port_box)

        self.v_layout.addWidget(self.connection_btn)
        self.setLayout(self.v_layout)

        self.resize(400, 150)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('Hand Washing Experiment')

        self.show()

    def connection(self):
        if str(self.ip_address.text()) == '' or str(self.ip_port.text()) == '':
            warning_box = QMessageBox()
            warning_box.setText('Please enter IP Address and/or target Port ')
            warning_box.setStandardButtons(QMessageBox.Ok)
            warning_box.exec()
        else:
            port = int(self.ip_port.text())
            ip_address = self.ip_address.text()

            try:
                s.connect((ip_address, port))
            except:
                warning_box = QMessageBox()
                warning_box.setText('Wrong IP Address and/or Port ')
                warning_box.setStandardButtons(QMessageBox.Ok)
                warning_box.exec()
                sys.exit()

            self.close()

    # def closeEvent(self, QCloseEvent):
    #     sys.exit()


class HandWashingCollector(QWidget):

    def __init__(self, pipe, s):
        super().__init__()

        self.pipe = pipe
        self.s = s
        self.position_list = ['left-UpperArm left-LowerArm right-UpperArm right-LowerArm']
        self.video_type_list = ['With Demonstration', 'Without Demonstration', 'Poster']
        self.input_width = 300

        self.v_layout = QVBoxLayout()
        self.line_edit = QLineEdit(self)
        self.experiment = QLineEdit(self)
        self.combobox_position = QComboBox(self)
        self.combobox_type = QComboBox(self)
        self.begin_button = QPushButton('Begin Experiment')
        self.begin_button.clicked.connect(self.button_func)

        self.player = []

        self.init_ui()

    def init_ui(self):
        self.layout_init()
        self.combobox_init()

        self.resize(400, 300)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topRight())
        self.setWindowTitle('Hand Washing Experiment')

        self.show()

    def layout_init(self):
        experiment_box = QHBoxLayout()
        experiment_box.addWidget(QLabel('Participant Name:'))
        self.line_edit.setFixedWidth(self.input_width)
        experiment_box.addWidget(self.line_edit, alignment=Qt.AlignHCenter)
        self.v_layout.addLayout(experiment_box)

        name_box = QHBoxLayout()
        name_box.addWidget(QLabel('Experiment Times:'))
        self.experiment.setFixedWidth(self.input_width)
        name_box.addWidget(self.experiment, alignment=Qt.AlignHCenter)
        self.v_layout.addLayout(name_box)

        position_box = QHBoxLayout()
        position_box.addWidget(QLabel('Armband Position:'))
        self.combobox_position.setFixedWidth(self.input_width)
        position_box.addWidget(self.combobox_position, alignment=Qt.AlignHCenter)
        self.v_layout.addLayout(position_box)

        type_box = QHBoxLayout()
        type_box.addWidget(QLabel('Display Type:'))
        self.combobox_type.setFixedWidth(self.input_width)
        type_box.addWidget(self.combobox_type, alignment=Qt.AlignHCenter)
        self.v_layout.addLayout(type_box)

        self.v_layout.addWidget(self.begin_button)

        self.setLayout(self.v_layout)

    def combobox_init(self):
        self.combobox_position.addItems(self.position_list)
        self.combobox_type.addItems(self.video_type_list)

    def button_func(self):
        if str(self.line_edit.text()) == '' or str(self.experiment.text()) == '':
            warning_box = QMessageBox()
            warning_box.setText('Please enter the participant\'s name\nand the experiment times')
            warning_box.setStandardButtons(QMessageBox.Ok)
            warning_box.exec()
        else:
            if 'Demonstration' in (str(self.combobox_type.currentText())):
                player = vlc_player.Player()
                player.set_pipe(self.pipe, self.s)

                self.connection()

                self.player.append(player)
                player.show()
                player.resize(1200, 800)

                if (str(self.combobox_type.currentText())) == 'With Demonstration':
                    player.OpenFile('../resource/Video_withDemon.mp4')
                else:
                    player.OpenFile('../resource/Video_withoutDemon.mp4')

            else:
                handwashing_poster = poster.Poster()
                handwashing_poster.set_pipe(self.pipe, self.s)

                self.connection()
                self.player.append(handwashing_poster)
                handwashing_poster.show()

    def connection(self):
        now = datetime.datetime.timestamp(datetime.datetime.now())
        _, time_offset = project_library.get_time_offset()
        sleep_time = now + time_offset + 5

        result = json.dumps({
                'status': 'start',
                'time': sleep_time,
                'message': {'status': 'start', 'participant_name': str(self.line_edit.text()),
                            'experiment_times': str(self.experiment.text()),
                            'position': str(self.combobox_position.currentText()),
                            'video_type': str(self.combobox_type.currentText())}
        })

        if self.s is not None:
            self.s.send(result.encode())

        sleep_diff = sleep_time - datetime.datetime.timestamp(datetime.datetime.now())
        time.sleep(sleep_diff)

        self.pipe.send({'status': 'start', 'participant_name': str(self.line_edit.text()),
                        'experiment_times': str(self.experiment.text()),
                        'position': str(self.combobox_position.currentText()),
                        'video_type': str(self.combobox_type.currentText())})


def plot_emg(pipe):
    if sys.platform.startswith('win'):
        path = '../myo_sdk/sdk_windows'
        start_num, end_num = 1, 2
    elif sys.platform.startswith('darwin'):
        path = '../myo_sdk/sdk_macos'
        start_num, end_num = 3, 4

    myo.init(sdk_path=path)
    hub = myo.Hub()
    listener = collect_data.DataCollector(512, start_num, end_num)
    with hub.run_in_background(listener.on_event):
        collect_data.Plot(listener).data_plot(pipe)


def interface(pipe, s):
    app = QApplication(sys.argv)
    collector = HandWashingCollector(pipe, s)
    sys.exit(app.exec_())


def main():
    pipe_emg, pip_interface = Pipe()

    process_emg = Process(target=plot_emg, args=(pipe_emg,))
    process_interface = Process(target=interface, args=(pip_interface, s))
    process_emg.start()
    process_interface.start()
    process_emg.join()
    process_interface.join()


s = socket.socket()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    collector = IPCollector()
    app.exec_()

    main()
