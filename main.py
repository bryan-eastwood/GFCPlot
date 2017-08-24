import matplotlib.pyplot as plt
import operator
import csv
import sys
import time
import datetime
from calendar import timegm
from matplotlib.ticker import FuncFormatter
import parser
import math
from threading import Thread
from time import sleep
import urllib
import codecs
import os

PROMPT_FOR_BOUNDS = False
DEFAULT_INPUT_FILENAME = "data.csv"

devices = {}
most_recent = 0

def ticker_function(epoch, pos):
        win_offset = 4*3600000/1000
        if os.name != "nt":
                win_offset = 0
        try:
                return (datetime.datetime.fromtimestamp(epoch + win_offset)).strftime('%a %d %H:%M')
        except OSError:
                return ""

def plot_coords(ax, coords, label):
        return ax.plot(list(map(lambda x: x[0], coords)),
		 	list(map(lambda x: x[1], coords)),
			label=label)

def add_row(name, date, temp):
	global most_recent
	print([date, temp])
	if(date > most_recent):
		most_recent = date
	if(not name in devices):
		devices[name] = []
	devices[name].append([date, temp])

def get_epoch(timestamp):
	#return timegm(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"))
	return timegm(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ"))


def limit_range(begin, end):
	for device in devices:
		temp = []
		for row in devices[device]:
			if(row[0] >= begin and row[0] <= end):
				temp.append(row)
		devices[device] = temp

print("Reading...", end="")
sys.stdout.flush()

data = csv.reader(codecs.iterdecode(urllib.request.urlopen("http://10.199.251.176:44449/GFC_data.csv"), 'utf-8'), delimiter=",")
for row in data:
	add_row(row[1].strip(" \""), get_epoch(row[0]), row[2])

print(" DONE")

fig, ax = plt.subplots();

ax.set_ylabel('Temperature (\N{DEGREE SIGN}F)')
ax.xaxis.set_major_formatter(FuncFormatter(ticker_function));
plt.xticks(rotation=70)
#fig.tight_layout()
fig.subplots_adjust(bottom=0.2)

if PROMPT_FOR_BOUNDS:
	lower = input("Lower Bound: ")
	lower = int(parser.parse(lower).strftime("%s")) * 1000 if lower else 0
	upper = input("Upper Bound: ")
	upper = int(parser.parse(upper).strftime("%s")) * 1000 if upper else math.inf

	limit_range(lower, upper)

lines = []
for name, data in sorted(devices.items(), key=operator.itemgetter(0)):
	lines.append(plot_coords(ax, data, name))

leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
      		ncol=3, fancybox=True, shadow=True)

leg.get_frame().set_alpha(0.4)
lined = dict()
for legline, origline in zip(leg.get_lines(), lines):
    legline.set_picker(5)  # 5 pts tolerance
    lined[legline] = origline


def onpick(event):
    legline = event.artist
    origline, = lined[legline]
    vis = not origline.get_visible()
    origline.set_visible(vis)
    if vis:
        legline.set_alpha(1.0)
    else:
        legline.set_alpha(0.2)
    fig.canvas.draw()

fig.canvas.mpl_connect('pick_event', onpick)

def update_temp():
	while(True):
		print("Querying...")
		data = csv.reader(codecs.iterdecode(urllib.request.urlopen("http://10.199.251.176:44449/GFC_data.csv"), 'utf-8'), delimiter=",")
		for row in data:
			date = get_epoch(row[0])
			print("%d > %d" % (date, most_recent))
			if(date > most_recent):
				add_row(row[1].strip(" \""), date, row[2]);
		print("Done")

		current_temps = []
		for name, data in sorted(devices.items(), key=operator.itemgetter(0)):
			current_temps.append([name, float(data[-1][1])])
		label = ", ".join('%s: %.2f' % (x[0], x[1]) for x in current_temps)
		index = label.find(',', int(len(label)/2)) + 2
		ax.set_xlabel(label[:index] + '\n' + label[index:])
		fig.canvas.draw()
		time.sleep(1)

thread = Thread(target = update_temp)

thread.start()

plt.show()
