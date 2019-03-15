import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDesktopWidget
from PyQt5.QtGui import QIcon, QPixmap


class Poster(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Handwashing Poster'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.pipe = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create widget
        label = QLabel(self)
        pixmap = QPixmap('../resource/handwashing.png')
        label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topRight())

        self.show()

    def set_pipe(self, pipe):
        self.pipe = pipe

    def closeEvent(self, *args, **kwargs):
        if self.pipe is not None:
            self.pipe.send({'status': 'end'})

        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Poster()
    sys.exit(app.exec_())
