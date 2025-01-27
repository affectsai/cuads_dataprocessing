import csv
import json
import sys
import matplotlib.pyplot as plt
import numpy as np

results = {}
with open(sys.argv[1],'r') as all_responses_file:
    reader = csv.reader(all_responses_file, delimiter=',')
    next(reader)    # Skip header line...

    for line in reader:
        if line[1] not in results:
            results[line[1]] = []

        results[line[1]].append([float(line[2]),float(line[3])])

print(json.dumps(results))

for key in results:
    # Create the plot
    fig,ax = plt.subplots()

    xdata = [point[0] - 5 for point in results[key]]
    ydata = [point[1] - 5 for point in results[key]]
    xmean = np.mean(xdata)
    ymean = np.mean(ydata)

    ax.scatter(xdata, ydata)
    ax.scatter([xmean],[ymean], color='red',marker='x')
    # ax.plot([0,0],[-5,5])
    # ax.plot([-5,5],[0,0])
    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.axhline(y=0, color='k')
    ax.axvline(x=0, color='k')
    ax.set_xlabel('Valence')
    ax.set_ylabel('Arousal')
    ax.set_title(key)

    # Display the plot
    plt.savefig(f'{key}.png')