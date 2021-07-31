import pyawr.mwoffice as mwo
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation 

awrde = mwo.CMWOffice() #Create awrde object

awrde.Project.Simulator.Analyze()

graph_name = awrde.Project.Graphs.Item(2).Name
graph = awrde.Project.Graphs(graph_name)
meas = graph.Measurements[0]

print(meas.Name)

fig = plt.figure()
ax = plt.subplot(1,1,1)

# trace, = ax.plot([])

num_pts = meas.XPointCount
xs = ys = np.zeros(num_pts)

def animate(n_frm):
    xs = meas.XValues
    ys = meas.YValues(1)

    # trace.set_data(xs, ys)

    ax.cla()
    ax.plot(xs, ys)

    # return [trace]

#TODO: Figure out this blit thing
ani = FuncAnimation(fig, animate, interval=200, blit=False)
plt.show()
