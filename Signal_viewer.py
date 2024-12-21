from oscpy.server import OSCThreadServer  # type: ignore
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from utilities import HighPassFilter, LowPassFilter
import numpy as np
import socket

#get local ip (this function was made by chatgpt)
def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception as e:
        return f"Erreur : {e}"

# show local IP (these 2 lines were made by chatgpt)
local_ip = get_local_ip()
print("\nYour IP address is:", local_ip, "\nPlease enter your IP address in the Comote app OSC settings.\n")

# creates OSC server
osc = OSCThreadServer(encoding="utf8")
osc.listen(address=local_ip, port=8001, default=True)

print("Listening for OSC messages...")

N = 100  # Window size
signal_filtered = [0] * N
fcHP = 1  # cutoff frequency, High Pass filter
fcLP = 25  # cutoff frequency, Low Pass filter

hpfilter = HighPassFilter(fcHP, 0.010)
lpfilter = LowPassFilter(fcLP, 0.010)

def get_acceleration(*values):
    global signal, signal_filtered, RC
    hpfilter.dt = values[0]*10**(-3)  #time interval
    filtered_value = values[3]
    print(values,end="\r")
    signal_filtered.append(filtered_value)
    signal_filtered = signal_filtered[-N:]  #only keep window size array
    osc.send_message('/intensity', (filtered_value, ), "0.0.0.0", 8098)

osc.bind('/comote/0/devicemotion', get_acceleration)

fig, ax = plt.subplots()
line, = ax.plot(range(N), signal_filtered)
ax.set_ylim(-50, 50)
ax.set_xlim(0, N)

def update_plot(frame):
    line.set_ydata(signal_filtered) 
    return line,


anim = FuncAnimation(fig, update_plot, interval=1000 / 24, blit=True)
plt.show()


osc.stop_all()
osc.terminate_server()
osc.join_server()
print("Stopped.")
