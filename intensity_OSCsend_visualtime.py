from oscpy.server import OSCThreadServer  # type: ignore
import matplotlib.pyplot as plt
from utilities import HighPassFilter, LowPassFilter, get_local_ip, Buffer, Visualizer



# show local IP (these 2 lines were made by chatgpt)
local_ip = get_local_ip()
print("\nYour IP address is:", local_ip, "\nPlease enter your IP address in the Comote app OSC settings.\n")

# creates OSC server
osc = OSCThreadServer(encoding="utf8")
osc.listen(address=local_ip, port=8001, default=True)
print("Listening for OSC messages...")

N = 2
M = 128 # buffer size: 32, 64, 128, 256, 512, and 1024
fcHP = 1  # cutoff frequency, High Pass filter
fcLP = 25  # cutoff frequency, Low Pass filter
dt_init=0.01

buffer_unfiltered = Buffer(N, M) # unfiltered signal
buffer_filtered = Buffer(N, M) # filtered signal
hpfilter = HighPassFilter(fcHP, dt_init) # creating filters
lpfilter = LowPassFilter(fcLP, dt_init) 
visualizer = Visualizer(buffer_filtered, 1) # creating graphs


def get_acceleration(*values):
    buffer_unfiltered.push(values[:N])
    #dt update for filters
    hpfilter.dt = buffer_unfiltered[0,-1] * 10**(-3)  # Intervalle de temps
    lpfilter.dt = buffer_unfiltered[0,-1] * 10**(-3)  # Intervalle de temps

    filtered_value = lpfilter.apply(hpfilter.apply(buffer_unfiltered[1, -1]))
    new_row = [buffer_unfiltered[0, -1], filtered_value]
    buffer_filtered.push(new_row)
    #sending OSC to ableton
    osc.send_message('/intensity', (buffer_filtered[1, -1], ), "127.0.0.1", 8098)


#everytime an OSC message is received, the given function is called
osc.bind('/comote/0/devicemotion', get_acceleration)
#show
animation = visualizer.plot_time(duration=400, refresh_rate=24)
#animation_fft = visualizer.plot_fft( 0, 20,  0,  25)
plt.show()  # Blocks server, showing the visualization



osc.stop_all()
osc.terminate_server()
osc.join_server()
print("Stopped.")