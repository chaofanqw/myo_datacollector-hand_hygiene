import sys
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication, QComboBox, \
                            QLineEdit, QVBoxLayout, QMessageBox, QHBoxLayout, \
                            QLabel, QPushButton
from PyQt5.QtCore import Qt
import methods.vlc_player as vlc_player
import methods.collect_data as collect_data
import myo
from multiprocessing import Process

"""
In Windows, please install vlc(x64) from https://www.videolan.org/vlc/download-windows.html ,
and set the environment path: PYTHON_VLC_MODULE_PATH: C:\Program Files\VideoLAN\VLC or other installed index;

In MacOS, it will be necessary install vlc by homebrew, with
brew cask install vlc
"""


class HandWashingCollector(QWidget):

    def __init__(self):
        super().__init__()

        self.position_list = ['Wrist', 'Upper Arm', 'Lower Arm']
        self.video_type_list = ['With Demonstration', 'Without Demonstration']
        self.input_width = 200

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
        self.move(qr.topLeft())
        self.setWindowTitle('Hand Washing Experiment')

        self.show()

    def layout_init(self):
        experiment_box = QHBoxLayout()
        experiment_box.addWidget(QLabel('Participant Name:'))
        self.line_edit.setFixedWidth(self.input_width - 10)
        experiment_box.addWidget(self.line_edit, alignment=Qt.AlignHCenter)
        self.v_layout.addLayout(experiment_box)

        name_box = QHBoxLayout()
        name_box.addWidget(QLabel('Experiment Times:'))
        self.experiment.setFixedWidth(self.input_width - 10)
        name_box.addWidget(self.experiment, alignment=Qt.AlignHCenter)
        self.v_layout.addLayout(name_box)

        position_box = QHBoxLayout()
        position_box.addWidget(QLabel('Armband Position:'))
        self.combobox_position.setFixedWidth(self.input_width)
        position_box.addWidget(self.combobox_position, alignment=Qt.AlignHCenter)
        self.v_layout.addLayout(position_box)

        type_box = QHBoxLayout()
        type_box.addWidget(QLabel('Video Type:'))
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
            player = vlc_player.Player()
            self.player.append(player)
            player.show()
            player.resize(640, 480)
            player.OpenFile('../resource/Video_withDemon.mp4')


def plot_emg():
    myo.init(sdk_path='../myo_sdk/sdk_windows')
    hub = myo.Hub()
    listener = collect_data.DataCollector(512)
    with hub.run_in_background(listener.on_event):
        collect_data.Plot(listener).main()


def interface():
    app = QApplication(sys.argv)
    collector = HandWashingCollector()
    sys.exit(app.exec_())


def main():
    process_emg = Process(target=plot_emg)
    process_interface = Process(target=interface)

    process_emg.start()
    process_interface.start()

    process_emg.join()
    process_interface.join()


if __name__ == '__main__':
    main()
