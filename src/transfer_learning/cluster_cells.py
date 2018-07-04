import csv
import numpy as np

import matplotlib 
matplotlib.use('agg')
import  matplotlib.pyplot as plt 

import pylab 
import scipy  

from scipy.cluster.hierarchy import dendrogram, linkage, fcluster 

# cut-off threshold for clustering 
CLUSTER_NUMBER = 20 

# define euclidean distance metric for measure disimilarity 
def distance (a, b) :
    return np.sqrt(np.sum(np.remainder(np.add(a,b), 2)))

# read the cell target labels into array (n (#cells) x m (# regions))
cell_array = [] 
counter = 0
with open("/srv/scratch/xnancy/labeled/intervals_files_complete.tsv") as tsv:
    # for column in zip(*[line for line in csv.reader(tsv, delimiter="\t")]):
    for row in csv.reader(tsv, delimiter="\t"): 
        counter = counter + 1
        cell_array.append(row[3:]) 

cell_array_arr = np.asarray(cell_array)
cell_array_arr = np.transpose(cell_array_arr) 
np.savetxt("cell_array_transposed.csv", cell_array_arr, fmt='%5s', delimiter=",")

# build linkage matrix from the cells 
Y = linkage(cell_array_arr, 'ward')
Y_arr = np.asarray(Y)
np.savetxt("linkage_matrix.csv", Y_arr, delimiter=",")

print "saved linkage"

# perform hierarchical clustering of the data 
data_clusters = fcluster(Y, CLUSTER_NUMBER, criterion="maxclust")
data_clusters_arr = np.asarray(data_clusters) 
np.savetxt("data_clusters.csv", data_clusters_arr, delimiter=",")
 
# create plot of hierarchical clustering 
fig = pylab.figure(figsize=(8,8))

plt.title('Binding Site Variations in 431 Cell Types')

# Plot first dendrogram 
ax1 = fig.add_axes([0.09,0.1,0.2,0.6])
Z1 = dendrogram(Y, orientation='right')
ax1.set_xticks([])
ax1.set_yticks([])

# Compute and plot second dendrogram.
ax2 = fig.add_axes([0.3,0.71,0.6,0.2])
Z2 = dendrogram(Y)
ax2.set_xticks([])
ax2.set_yticks([])

# Plot distance matrix.
distance_matrix = distance_matrix(cell_array_arr, cell_array_arr)
"""
distance_matrix = np.zeros((len(cell_array_arr), len(cell_array_arr)))
for i in range(len(cell_array_arr)): 
    for j in range(i): 
        distance_matrix[i][j] = distance(cell_array_arr[i].astype(float), cell_array_arr[j].astype(float))
        distance_matrix[j][i] = distance_matrix[i][j]
"""

axmatrix = fig.add_axes([0.3,0.1,0.6,0.6])
idx1 = Z1['leaves']
D = np.asarray(distance_matrix)
D = D[idx1,:]
D = D[:,idx1]
im = axmatrix.matshow(D, aspect='auto', origin='lower', cmap=pylab.cm.YlGnBu)
axmatrix.set_xticks([])
axmatrix.set_yticks([])

# Plot colorbar.
axcolor = fig.add_axes([0.91,0.1,0.02,0.6])
pylab.colorbar(im, cax=axcolor)
fig.savefig('dendrogram.png')


############
# fig = pylab.figure()
# axdendro = fig.add_axes([0.09,0.1,0.2,0.8])
# Z = dendrogram(Y_array, orientation='right')
# axdendro.set_xticks([])
# axdendro.set_yticks([])

# Plot distance matrix.
# axmatrix = fig.add_axes([0.3,0.1,0.6,0.8])
# index = Z['leaves']
# print index 
# cell_array = cell_array[index,:]
# cell_array = cell_array[:,index]
# im = axmatrix.matshow(cell_array, aspect='auto', origin='lower')
# axmatrix.set_xticks([])
# axmatrix.set_yticks([])

# Plot colorbar.
# axcolor = fig.add_axes([0.91,0.1,0.02,0.8])
# pylab.colorbar(im, cax=axcolor)

# Display and save figure.
# fig.savefig('dendrogram.png')

