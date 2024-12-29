import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import socket

class Buffer:
    def __init__(self, N, M):
        self.line_number = N
        self.column_number = M
        self.buffer = np.zeros((N, M))

    def push(self, signal):
        if isinstance(signal, float):
            self.buffer = np.roll(self.buffer, -1, axis=1)
            self.buffer[:, -1] = signal
        elif len(signal) == self.line_number:
            self.buffer = np.roll(self.buffer, -1, axis=1)
            self.buffer[:, -1] = signal
        else:
            raise ValueError(f"Expected data of length {self.line_number} or a float, but got {type(signal).__name__}")
        
    def __getitem__(self, index):
        return self.buffer[index]
    
    #to print
    def __str__(self):
        buffer_preview = np.array_str(self.buffer, precision=2, suppress_small=True)
        return (f"Buffer with shape ({self.line_number}, {self.column_number}):\n"
                f"{buffer_preview}")

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
    
class Intensity:
    def __init__(self, average_count, raw_datas):
        self.raw_datas = raw_datas
        self.buffer = Buffer(1, average_count) #change avarage value

    def mai(self):
        intensity_sample = np.linalg.norm(self.raw_datas[1:,-1])
        self.buffer.push(intensity_sample)
        return np.mean(self.buffer.buffer)
    
    def mai_noaverage(self):
        intensity_sample = np.linalg.norm(self.raw_datas[1,-1])
        return intensity_sample

class Visualizer:
    def __init__(self, buffer, direction, dt_initial):
        self.buffer = buffer
        self.fig, self.ax = plt.subplots()
        self.line = None  # Initialiser la ligne
        self.direction = direction
        self.dt_initial = dt_initial

    def plot_time(self, duration = 15, refresh_rate = 24 ):
        time_list = np.cumsum(self.buffer[0, :])
        point_list = self.buffer[self.direction,0:]
        self.line = self.ax.plot(time_list, point_list)[0]
        self.ax.set_xlim([0, duration])  # Limites initiales de l'axe x
        self.ax.set_ylim([-30, 30])  # Limites initiales de l'axe y
        # Animation
        return FuncAnimation(self.fig, self.update_plot_time, frames = duration * refresh_rate, interval=1000 / refresh_rate)

    def update_plot_time(self, frame, xrange = 15):
        # time_list = np.cumsum(self.buffer[0, :])
        # if time_list[0,-1] > xrange: #je veux a voir une fenêtre glissante
        #      self.ax.set_xlim(self.buffer[0,-1-xrange], self.buffer[0,-1])  # Décalage de l'axe
        # else:
        #     self.ax.set_xlim(0, xrange)
        
        # self.line.set_data(self.buffer[0, :], self.buffer[self.direction, :])
        # return self.line,
        time_list = np.cumsum(self.buffer[0, :])    
        # Vérification si la fenêtre glissante doit être appliquée
        # if time_list[-1] > xrange:
        #     # Déterminer l'index correspondant à la borne inférieure de la fenêtre
        #     start_index = np.searchsorted(time_list, time_list[-1] - xrange)
        #     time_window = time_list[start_index:]
        #     point_window = self.buffer[self.direction, start_index:]
        # else:
        #     # Si pas assez de temps pour une fenêtre complète, afficher tout
        #     time_window = time_list
        #     point_window = self.buffer[self.direction, :]

        # Mettre à jour les données du tracé
        point_window = self.buffer[self.direction, :]
        time_window = time_list

        self.line.set_data(time_window, point_window)
        # Mettre à jour les limites de l'axe x
        self.ax.set_xlim(time_window[0], time_window[-1])
        return self.line,

    def plot_fft(self, dt_initial, xrangemin = 0, xrangemax = 20,  yrangemin = 0,  yrangemax = 25):
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_xlabel('Frequency (Hz)')
        self.ax.set_ylabel('Amplitude')
        self.ax.set_title('Frequency Spectrum')
        # #Compute FFT 
        # fft_values = np.fft.fft(self.buffer[self.direction,0:])
        # amplitude_spectrum = np.abs(fft_values) / len(fft_values)
        # frequencies = np.fft.fftfreq(len(fft_values), dt_initial)
        # # Update line data
        # self.line.set_data(frequencies[:len(frequencies)//2], amplitude_spectrum[:len(amplitude_spectrum)//2])
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 25)
        return FuncAnimation(self.fig, self.update_plot_fft, interval=1000/24, blit=True, cache_frame_data=False)
                                                                                                                                        
    # Fonction interne pour mettre à jour l'animation
    def update_plot_fft(self, frame):
        dt_average = np.mean(self.buffer[0,0:])*10**(-3) #ms to s
        if dt_average <= 0:
            dt_average = self.dt_initial
        # Calcul de la FFT
        fft_values = np.fft.fft(self.buffer[self.direction,0:])
        amplitude_spectrum = np.abs(fft_values) / len(fft_values)
        frequencies = np.fft.fftfreq(len(fft_values), dt_average)
        # Mise à jour des données de la ligne
        self.line.set_data(frequencies[:len(frequencies)//2], amplitude_spectrum[:len(amplitude_spectrum)//2])
        return self.line,

#get local ip (this function was made by chatgpt)
def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception as e:
        return f"Erreur : {e}"