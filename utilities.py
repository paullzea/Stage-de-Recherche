import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


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