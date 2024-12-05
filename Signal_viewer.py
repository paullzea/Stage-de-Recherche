from oscpy.server import OSCThreadServer  # type: ignore
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
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

# Create server and start listening
osc = OSCThreadServer(encoding="utf8")
osc.listen(address=get_local_ip(), port=8001, default=True)

print("listening")

N=100
signal = [0 for i in range(0,N)]

def get_acceleration(*values):
    signal.append(values[1])

osc.bind('/comote/0/devicemotion', get_acceleration)

fig, ax = plt.subplots()
line = ax.plot(signal)[0]
ax.set_ylim(-50, 50)



def update_plot(frame):
    line.set_xdata([i for i in range(len(signal)-N,len(signal))])
    line.set_ydata(signal[-N:])
    ax.set_xlim(len(signal)-N, len(signal))
    return line,

anim = FuncAnimation(fig, update_plot, interval=1000/24, blit=True)
plt.show()

print("stopped")
# Stop all server threads and processes properly after animation is closed
osc.stop_all()
osc.terminate_server()
osc.join_server()