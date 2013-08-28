'''
Experimental set of tools for generating plots of usage stats. 

While not the most efficient workflow, this is much easier to implement
as it does not require any changes to the existing code for generating usage
stats
'''

import os
import argparse
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

def parse_usage_from_txt(fname):
	'''
	Parses usage stats from a given file (usually generated from a given tier, eg
	ou.txt) and stores them in a dictionary for easier handling later. 
	'''
	tier = fname.replace('/', '.').split('.')[-2]
	usage_dict = {'ranks': [], 'pokes': [], 'usage': [], 'raw': [], 
				  'raw_perc': [], 'real': [], 'real_perc': [], 'tier' : tier}
	with open(fname) as tf:
		for lno, line in enumerate(tf.readlines()):
			line = line.rstrip()
			if lno == 0:
				usage_dict['total'] = int(line.split(' ')[-1])
			elif lno == 1:
				usage_dict['weight'] = float(line.split(' ')[-1])
			elif lno == 3 or '+' in line:
				continue
			else:
				line = line.replace(' ', '')
				line = line.replace('%', '')
				info = line.split('|')[1:-1]
				usage_dict['ranks'].append(int(info[0]))
				usage_dict['pokes'].append(info[1])
				usage_dict['usage'].append(float(info[2]))
				usage_dict['raw'].append(int(info[3]))
				usage_dict['raw_perc'].append(float(info[4]))
				usage_dict['real'].append(int(info[5]))
				usage_dict['real_perc'].append(float(info[6]))
				
	return usage_dict
	
def plot_usage(usage_dict, hi=1, lo=None):
	'''
	Plot a horizontal bar chart showing the usage for each pokemon for the 
	given statistic. usage_dict is a dictionary that should be generated 
	from parsing the usage text file for a tier. lo and hi represent the range
	of Pokemon (by rank) that will be shown in the plot. For example, to plot
	the top 50, hi = 1 and lo = 50.
	
	For now this only plots usage %. However support for plotting other data
	can be easily added later if needed.
	'''
	# lo defaults to the total number of pokemon
	if lo is None:
		lo = len(usage_dict['pokes'])
		
	ranks = usage_dict['ranks']
	# Make sure lo and hi are valid
	if lo not in ranks or hi not in ranks:
		raise ValueError('Invalid input for lo and or hi')
	
	# Subset the data so we only plot ranks we want
	slc = slice(hi - 1, lo)
	usage = usage_dict['usage'][slc][::-1]
	pokes = usage_dict['pokes'][slc][::-1]
	tier = usage_dict['tier']
	total = usage_dict['total']
	weight = usage_dict['weight']
	npokes = lo - hi + 1
	y_pos = range(npokes)
	
	# Make the figure. Vertical extent will depend on the number
	# of Pokemon included in the analysis.
	density = (npokes / 25.) # Roughly 5 pokemon per 200 pixels
	width, height = 8, 6 * density
	fig = plt.figure(figsize=(width, height))
	
	# For now just one subplot. 
	ax = fig.add_subplot(111)
	
    # Our graph of choice is a bar chart. Purple for smogon spirit!
	rects = ax.barh(y_pos, usage, align='center', facecolor='#A020F0')
	
	# Label the bars with their values so they are easier to interpret
	for perc, rect in zip(usage, rects):
		x = .98 * float(rect.get_width())
		y = rect.get_y() + rect.get_height() / 2.0
		ax.text(x, y, '%2.1f' %(perc), ha='right', va='center', color='w',
				size='xx-small')
	
	# Place Overall information in the title
	ax.set_title('Tier: %s (Rank %d-%d) \n'
				 'Total Battles: %d \n'
				 'Avg Weight / Team: %0.3f' %(tier, hi, lo, total, weight))
				 
	# Make sure everything is labeled correctly
	ax.yaxis.set_major_locator(MultipleLocator(1))
	ax.set_xlabel('Usage [%]')
	ax.set_yticks(y_pos)
	ax.set_yticklabels(pokes, size='xx-small')
	ax.yaxis.set_ticks_position('none')
	ax.set_ylim(y_pos[0] - 1, y_pos[-1] + 1)
	
	# Save the image to disk
	if not os.path.exists('figs'):
		os.makedirs('figs')
	fig.savefig('figs/%s_usage.png' %(tier), bbox_inches='tight')
	fig.clf()
	
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Script for plotting usage stats')
	parser.add_argument('-l', '--lower', default=50, action='store',
						type=int, help='Lowest rank to show')
	parser.add_argument('-u', '--upper', default=1, action='store', 
						type=int, help='Highest rank to show')
	parser.add_argument('fname', metavar='file', type=str,
						help='The text file containing the processed stats')
	args = parser.parse_args()
	lo, hi, fname = args.lower, args.upper, args.fname
	usage_dict = parse_usage_from_txt(fname)
	plot_usage(usage_dict, lo=lo, hi=hi)
