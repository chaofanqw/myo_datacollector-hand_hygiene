import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDesktopWidget
from PyQt5.QtGui import QIcon, QPixmap
import json
from methods import video_record


class Poster(QWidget):
    def __init__(self, video_name, type_name):
        super().__init__()
        self.title = 'Poster'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.pipe = None
        self.s = None
        self.recorder = video_record.videoRecorder(video_name)
        self.type_name = type_name
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create widget
        label = QLabel(self)
        if self.type_name == 'handwashing':
            pixmap = QPixmap('../resource/handwash.png')
        else:
            pixmap = QPixmap('../resource/handrub.png')

        label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topRight())

        # self.show()

    def start_record(self):
        self.recorder.start()

    def set_pipe(self, pipe, s):
        self.pipe = pipe
        self.s = s

    def closeEvent(self, *args, **kwargs):
        if self.pipe is not None:
            self.pipe.send({'status': 'end'})
            self.recorder.set_message()

        if not self.s is None:
            self.s.send(json.dumps({'status': 'end'}).encode())

        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Poster()
    sys.exit(app.exec_())
