from oscpy.server import OSCThreadServer
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import time
import socket

#getphoneIP
def get_local_ip():
    try:
        # Se connecter à une adresse externe (Google DNS ici)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Adresse IP et port ne sont pas réellement utilisés
            local_ip = s.getsockname()[0]  # Récupère l'adresse IP locale
        return local_ip
    except Exception as e:
        return f"Erreur : {e}"

print("\n", "Your IP address is:", get_local_ip(),"\n","please enter your IP address in the Comote app OSC settings \n \n")

#constants
period = 10**-3
fs = 1 / period
buffer_size = 500

# Create and start OSC server
osc = OSCThreadServer(encoding="utf8")
osc.listen(address=get_local_ip(), port=8001, default=True)
print("listening")

# Initialize signal buffer
signal = [0] * buffer_size
t=[0] * buffer_size
i=0

# Update function for incoming OSC messages
def get_acceleration(*values):
    global signal
    t=time.time() #only for delta_t
    signal.append(values[1])

#every time an osc devicemotion comes, the get_acceleration fonction is called
osc.bind('/comote/0/devicemotion', get_acceleration)

# Setup Matplotlib figure
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2) #empty lists because no initial x and y data for the line, lw defines line width
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Amplitude')
ax.set_title('Frequency Spectrum')

# Update function for animation
def update_plot(frame):
    global signal
    global fs
    signal_buffered=signal[-buffer_size:len(signal)]
    # Compute FFT
    delta_t_average=(t[buffer_size-1]-t[0])/(buffer_size-1)
    if(len(t) > buffer_size):
        fs=1/delta_t_average
    fft_values = np.fft.fft(signal_buffered)
    amplitude_spectrum = np.abs(fft_values) / len(fft_values)
    frequencies = np.fft.fftfreq(len(fft_values), 1 / fs)
    
    # Update line data
    line.set_data(frequencies[:len(frequencies)//2], amplitude_spectrum[:len(amplitude_spectrum)//2])
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 25)
    signal_buffered.clear()
    return line,

# Animation
anim = FuncAnimation(fig, update_plot, interval=1000/24, blit=True)
plt.show()

# Cleanup after stopping
osc.stop_all()
osc.terminate_server()
osc.join_server()
print("stopped")