import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import socket
import time

"""
def fft_animation(signal, dt, ax, fig, buffer_size):
    line, = ax.plot([], [], lw=2) #empty lists because no initial x and y data for the line, lw defines line width
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude')
    ax.set_title('Frequency Spectrum')
    #Show FFT
    def plot_fft(signal, dt, ax, line):
        #Compute FFT
        fft_values = np.fft.fft(signal)
        amplitude_spectrum = np.abs(fft_values) / len(fft_values)
        frequencies = np.fft.fftfreq(len(fft_values), dt)
        # Update line data
        line.set_data(frequencies[:len(frequencies)//2], amplitude_spectrum[:len(amplitude_spectrum)//2])
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 25)
    # Update function for animation
    def update_plot(frame, buffer_size=buffer_size, ax=ax, line=line):
        buffer = signal[-buffer_size:]
        dtt = dt[-buffer_size:]
        #Redefine delta t for precision over OSC communication speed
        delta_t_average = np.mean(dtt)
        plot_fft(buffer, delta_t_average, ax, line)
        return line,
    return FuncAnimation(fig, update_plot, interval=1000/24, blit=True)
"""

class HighPassFilter:
    def __init__(self, cutoff_frequency, dt):
        self.fc = cutoff_frequency
        self.rc = 1 / (2 * np.pi * self.fc)
        self.dt = dt
        self.previous_output = 0
        self.previous_sample = 0

    def apply(self, sample):
        alpha = self.rc / (self.rc + self.dt)
        filtered_sample = alpha * (self.previous_output + sample - self.previous_sample)
        self.previous_output = filtered_sample
        self.previous_sample = sample
        return filtered_sample
    
class LowPassFilter:
    def __init__(self, cutoff_frequency, dt):
        self.fc = cutoff_frequency
        self.rc = 1 / (2 * np.pi * self.fc)
        self.dt = dt
        self.previous_output = 0
        self.previous_sample = 0

    def apply(self, sample):
        alpha = self.dt / (self.rc + self.dt)
        filtered_sample = alpha * sample + (1-alpha) * self.previous_sample
        self.previous_output = filtered_sample
        self.previous_sample = sample
        return filtered_sample

class Visualizer:
    def __init__(self, buffer, direction):
        self.buffer = buffer
        self.fig, self.ax = plt.subplots()
        self.line = None  # Initialiser la ligne
        self.direction = direction

    def plot_FFT(self, xrangemin = 0, xrangemax = 20,  yrangemin = 0,  yrangemax = 25 ):
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_xlabel('Frequency (Hz)')
        self.ax.set_ylabel('Amplitude')
        self.ax.set_title('Frequency Spectrum')
        self.ax.set_xlim(xrangemin, xrangemax)
        self.ax.set_ylim(yrangemin, yrangemax)
        
        return FuncAnimation(self.fig, self.update_plot_fft, interval=1000/24, blit=True) #si je return FuncAnimation il faudra créer dans le
                                                                                      #programme principale un objet anim = visualizer.plot_FFT(dt=0.1)
                                                                                      #puis exécuter plt.show
    # Fonction interne pour mettre à jour l'animation
    def update_plot_fft(self, frame):
        delta_t_average = np.mean(self.buffer[0,0:])
        # Calcul de la FFT
        fft_values = np.fft.fft(self.buffer[self.direction,0:])
        amplitude_spectrum = np.abs(fft_values) / len(fft_values)
        frequencies = np.fft.fftfreq(len(fft_values), delta_t_average)
        # Mise à jour des données de la ligne
        self.line.set_data(frequencies[:len(frequencies)//2], amplitude_spectrum[:len(amplitude_spectrum)//2])
        return self.line,
    
    def plot_time(self, duration = 15, refresh_rate = 24 ):
        time_list = self.buffer[0,0:]
        point_list = self.buffer[self.direction,0:]
        self.line = self.ax.plot(time_list, point_list)[0]
        self.ax.set_xlim([0, duration])  # Limites initiales de l'axe x
        self.ax.set_ylim([-20, 20])  # Limites initiales de l'axe y
        # Animation
        anim = FuncAnimation(self.fig, self.update_plot_time, frames = duration * refresh_rate, interval=1000 / refresh_rate) #autre méthode,
        plt.show()                                                                                      # la fonction ne renvoie rien mais lance 
                                                                                                        #automatiquement l'animation
                                                                                                        #quelle méthode est la mieux?
    def update_plot_time(self, frame, xrange = 15):
        if self.buffer[0,-1] > xrange: #je veux a voir une fenêtre glissante
             self.ax.set_xlim(self.buffer[0,-1-xrange], self.buffer[0,-1])  # Décalage de l'axe
        else:
            self.ax.set_xlim(0, xrange)
        
        self.line.set_data(self.buffer[0,0:],self.buffer[self.direction,0,:])
        return self.line,

#get local ip (this function was made by chatgpt)
def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception as e:
        return f"Erreur : {e}"