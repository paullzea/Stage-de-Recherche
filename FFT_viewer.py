
from oscpy.server import OSCThreadServer # type: ignore
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import time
import socket

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
line, = ax.plot([], [], lw=2) #empty lists because no initial x and y data for the line, lw defines line width
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Amplitude')
ax.set_title('Frequency Spectrum')

# Update function for animation
def update_plot(frame):
    global signal, fs, signal_buffered, signal_filtered, dt, dtt
    signal_buffered=signal[-buffer_size:len(signal)]
    dtt=dt[-buffer_size:len(dt)]
    #Redefine delta t for precision over OSC communication speed
    delta_t_average=np.mean(dtt)
    print(delta_t_average)
    #if(len(dt) > buffer_size):
    fs=1/delta_t_average
    
    #HP
    signal_filtered=[0] * buffer_size
    signal_filtered[0]=signal_buffered[0]
    HP(signal_buffered, delta_t_average)

    #Compute FFT
    fft_values = np.fft.fft(signal_filtered)
    amplitude_spectrum = np.abs(fft_values) / len(fft_values)
    frequencies = np.fft.fftfreq(len(fft_values), 1 / fs)
    
    # Update line data
    line.set_data(frequencies[:len(frequencies)//2], amplitude_spectrum[:len(amplitude_spectrum)//2])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 25)
    return line,

# Animation
anim = FuncAnimation(fig, update_plot, interval=1000/24, blit=True)

plt.show()

# Cleanup after stopping
osc.stop_all()
osc.terminate_server()
osc.join_server()
print("stopped")
