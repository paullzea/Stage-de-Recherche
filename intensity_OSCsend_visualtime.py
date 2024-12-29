from oscpy.server import OSCThreadServer  # type: ignore
import matplotlib.pyplot as plt
from utilities import HighPassFilter, LowPassFilter, get_local_ip, Buffer, Visualizer, Intensity

local_ip = get_local_ip()
print("\nYour IP address is:", local_ip, "\nPlease enter your IP address in the Comote app OSC settings.\n")

# creates OSC server
osc = OSCThreadServer(encoding="utf8")
osc.listen(address=local_ip, port=8001, default=True)
print("Listening for OSC messages...")

N = 4
M = 128 # buffer size: 32, 64, 128, 256, 512, and 1024
fcHP = 5  # cutoff frequency, High Pass filter
fcLP = 15  # cutoff frequency, Low Pass filter
fcHP_intensity = 1 # cutoff frequency, High Pass filter, intensity signal
dt_initial=0.004 # seconds
average_count = 10 # number of values used for signal averaging

buffer_unfiltered = Buffer(N, M) # unfiltered signal
buffer_filtered = Buffer(N, M) # filtered signal
intensity = Buffer(2,M)
hpfilter = HighPassFilter(fcHP, dt_initial) # creating filters
lpfilter = LowPassFilter(fcLP, dt_initial)
hpfilter_intensity = HighPassFilter(fcHP_intensity, dt_initial)
intensity_operator = Intensity(average_count, buffer_filtered)
visualizer = Visualizer(intensity, 1, dt_initial) # creating the graphs' outlines

def get_acceleration(*values):
    buffer_unfiltered.push(values[:N])
    #dt update for filters
    hpfilter.dt = buffer_unfiltered[0,-1] * 10**(-3)
    lpfilter.dt = buffer_unfiltered[0,-1] * 10**(-3)
    #filtering the 3 axis
    filtered_value1 = lpfilter.apply(hpfilter.apply(buffer_unfiltered[1, -1]))
    filtered_value2 = lpfilter.apply(hpfilter.apply(buffer_unfiltered[2, -1]))
    filtered_value3 = lpfilter.apply(hpfilter.apply(buffer_unfiltered[3, -1]))
    new_row = [buffer_unfiltered[0, -1], filtered_value1, filtered_value2, filtered_value3]
    buffer_filtered.push(new_row)
    intensity_sample = Intensity.mai(intensity_operator)
    filtered_intensity = hpfilter_intensity.apply(intensity_sample)
    new_row_intensity = [buffer_filtered[0, -1],filtered_intensity]
    intensity.push(new_row_intensity)
    #sending OSC to ableton
    osc.send_message('/intensity', (intensity[1, -1], ), "127.0.0.1", 8098)

osc.bind('/comote/0/devicemotion', get_acceleration) #everytime an OSC message is received, the given function is called
#show
animation = visualizer.plot_time(duration=400, refresh_rate=24)
#animation_fft = visualizer.plot_fft(dt_initial, 0, 20,  0,  25)
plt.show()  # Blocks server, showing the graphs

osc.stop_all()
osc.terminate_server()
osc.join_server()
print("Stopped.")