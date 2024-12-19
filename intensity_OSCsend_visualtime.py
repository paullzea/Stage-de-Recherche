from oscpy.server import OSCThreadServer  # type: ignore
from utilities import HighPassFilter, LowPassFilter, get_local_ip, Buffer, Visualizer


# show local IP (these 2 lines were made by chatgpt)
local_ip = get_local_ip()
print("\nYour IP address is:", local_ip, "\nPlease enter your IP address in the Comote app OSC settings.\n")

# creates OSC server
osc = OSCThreadServer(encoding="utf8")
osc.listen(address=local_ip, port=8001, default=True)
print("Listening for OSC messages...")

N = 100  # Window size
M = 4
fcHP = 1  # cutoff frequency, High Pass filter
fcLP = 25  # cutoff frequency, Low Pass filter
dt_init=0.01 

buffer_unfiltered = Buffer(N, M)
buffer_filtered = Buffer(N, 1)
hpfilter = HighPassFilter(fcHP, dt_init)
lpfilter = LowPassFilter(fcLP, dt_init)
visualizer = Visualizer(buffer_filtered)

def get_acceleration(*values):
    buffer_unfiltered.push(values[:M])
    hpfilter.dt = values[0]*10**(-3)  #time interval
    lpfilter.dt = values[0]*10**(-3)  #time interval
    filtered_value = values[1]
    filtered_value = hpfilter.apply(filtered_value)
    filtered_value = lpfilter.apply(filtered_value)
    buffer_filtered.push(filtered_value)
    osc.send_message('/intensity', (filtered_value, ), "127.0.0.1", 8098)
osc.bind('/comote/0/devicemotion', get_acceleration)

visualizer.plot_time()

osc.stop_all()
osc.terminate_server()
osc.join_server()
print("Stopped.")