
from oscpy.server import OSCThreadServer # type: ignore
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import time
import socket
from utilities import fft_animation

#getphoneIP
def get_local_ip():
    try:
        # Connects to an external adress (Google DNS here)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80)) 
            local_ip = s.getsockname()[0]  # Gets local IP
        return local_ip
    except Exception as e:
        return f"Erreur : {e}"

print("\n", "Your IP address is:", get_local_ip(),"\n","please enter your IP address in the Comote app OSC settings \n \n")

#constants
period = 10**-3
fs = 1 / period
buffer_size = 256
fc=2 #define the HP frequence 
RC=1/(2*np.pi*fc)
signal_filtered=[]
dt=[]

# Initialize signal buffer
signal = [0] * buffer_size
signal_filtered=[0] * buffer_size
i=0

#HP the given signal
def HP(signal, dt):
    global RC, signal_filtered
    alpha = RC / (RC + dt)
    for i in range(1, buffer_size):
        signal_filtered[i] = alpha * (signal_filtered[i-1] + signal[i] - signal[i-1])

# Create and start OSC server
osc = OSCThreadServer(encoding="utf8")
osc.listen(address=get_local_ip(), port=8001, default=True)
print("listening")

# Initialize signal buffer
signal = [0] * buffer_size
dtt=[0] * buffer_size
i=0

# Update function for incoming OSC messages
def get_acceleration(*values):
    global signal, dt
    signal.append(values[1])
    dt.append(values[0]*10**(-3))

#every time an osc devicemotion comes, the get_acceleration fonction is called
osc.bind('/comote/0/devicemotion', get_acceleration)

# Setup Matplotlib figure
fig, ax = plt.subplots()
anime = fft_animation(signal, dt, ax, fig, buffer_size)
print(type(anime))
plt.show()

# Cleanup after stopping
osc.stop_all()
osc.terminate_server()
osc.join_server()
print("stopped")
