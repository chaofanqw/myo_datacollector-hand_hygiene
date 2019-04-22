import cv2
from threading import Thread
import csv
import time


class videoRecorder(Thread):
    def __init__(self, document_name):
        super().__init__()
        self.message = False
        self.document_name = document_name

    def record_video(self):
        file = open(self.document_name.replace('.avi', '.csv'), 'w')
        csv_writer = csv.writer(file)
        csv_writer.writerow(['frame', 'time'])
        num = 0

        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'mpeg')
        out = cv2.VideoWriter(self.document_name, fourcc, 30, (640, 480))

        while True:
            ret, frame = cap.read()
            if ret:
                cv2.flip(frame, 1, frame)

                csv_writer.writerow([num, time.time()])
                num += 1
                out.write(frame)

                cv2.imshow("frame", frame)
                if cv2.waitKey(1) & self.message:
                    break
            else:
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def set_message(self):
        self.message = True

    def run(self):
        self.record_video()

#
# if __name__ == '__main__':
#     t = Thread(target=record_video, args=('../data/video.avi',))
#     t.start()
