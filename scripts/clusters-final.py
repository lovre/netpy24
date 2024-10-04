import os
from time import *

from matplotlib import pyplot as plt

import networkx as nx

from cdlib import algorithms
from cdlib.classes import *
from cdlib import viz

def read_pajek(file, path = '../nets'):
  """
  Read undirected multigraph with node clusters from Pajek file.
  """
  
  G = nx.MultiGraph(name = file)
  
  with open(os.path.join(path, file + '.net'), 'r') as file:
    nodes = {}
    for line in file:
      if line.startswith('*vertices'):
        continue
      elif line.startswith('*'):
        break
      else:
        node = line.strip().split('"')
        nodes[node[0].strip()] = node[1]
        G.add_node(node[1], cluster = int(node[2]) if len(node[2]) > 0 else 0)
        
    for line in file:
      edge = line.strip().split(' ')
      G.add_edge(nodes[edge[0]], nodes[edge[1]])
      
  return G
  
def known_clusters(G):
  """
  Clustering of undirected multigraph G from node attribute 'cluster'.
  """

  clusters = {}
  for i, data in G.nodes(data = True):
    c = data['cluster'] if 'cluster' in data else 0
    
    if c in clusters:
      clusters[c].append(i)
    else:
      clusters[c] = [i]
    
  return NodeClustering(list(clusters.values()), G, 'known')
  
def graph_info(G):
  """
  Print basic statistics of undirected multigraph G.
  """
  
  print("{:>15s} | '{:s}'".format('Graph', G.name))
  
  multi = False
  for edge in G.edges():
    if G.number_of_edges(edge[0], edge[1]) > 1:
      multi = True
      break
      
  print("{:>15s} | '{:s}'".format('Type', '===' if multi else '---'))
  
  n = len(G)
  m = G.number_of_edges()
  ks = [k for _, k in G.degree()]
  
  print("{:>15s} | {:,d} ({:,d})".format('Nodes', n, nx.number_of_isolates(G)))
  print("{:>15s} | {:,d} ({:,d})".format('Edges', m, nx.number_of_selfloops(G)))
  print("{:>15s} | {:.1f} ({:,d}, {:,d})".format('Degree', 2 * m / n, min(ks), max(ks)))
  
  CCs = sorted(nx.connected_components(G), key = len, reverse = True)

  print("{:>15s} | {:.1f}% ({:,d})\n".format('Components', 100 * len(CCs[0]) / n, len(CCs)))
  
def clusters_info(G, alg, label, k = 100):
  """
  Print basic statistics of clustering of undirected multigraph G.
  """
  
  print("{:>15s} | '{:s}'".format('Graph', G.name))
  print("{:>15s} | '{:s}' ({:d}x)".format('Algorithm', label, k))
  
  known = known_clusters(G)
  
  t, c, C, Q, NMI = 0, 0, 0, 0, 0
  for _ in range(k):
    tic = time()
    
    comms = alg(G)
    
    t += (time() - tic) # / k
    c += len(comms.communities) / k
    C += max(len(comm) for comm in comms.communities) / k
    Q += comms.newman_girvan_modularity().score / k
    NMI += known.normalized_mutual_information(comms).score / k
    
  print("{:>15s} | {:,.1f} x {:,.0f} ({:.1f}%)".format('Clusters', c, len(G) / c, 100 * C / len(G)))
  print("{:>15s} | {:.3f}".format('Q', Q))
  print("{:>15s} | {:.3f}".format('NMI', NMI))
  print("{:>15s} | {:.1f} sec\n".format('Time', t))
  
  return comms
  
def plot_block_model(G, comms):
  """
  Plot clustering of undirected multigraph G with block model.
  """

  nodes = [i for comm in comms.communities for i in comm]
  A = nx.adjacency_matrix(G, nodelist = nodes).todense()

  _, ax = plt.subplots()
  
  ax.imshow(A, cmap = 'binary', interpolation = 'nearest')
  
  xy = 0
  for comm in comms.communities[:-1]:
    xy += len(comm)
    ax.plot([xy - 0.5, xy - 0.5], [-0.5, len(G) - 0.5], '-r')
    ax.plot([-0.5, len(G) - 0.5], [xy - 0.5, xy - 0.5], '-r')
  
  ax.set_yticks(range(len(G)), labels = nodes, size = 'xx-small')
  ax.set_xticks(range(len(G)), labels = nodes, size = 'xx-small')
  plt.setp(ax.get_xticklabels(), rotation = 45, ha = 'right', rotation_mode = 'anchor')

#
# Small networks with known sociological partitioning
#

for file in ['karate', 'dolphins', 'women']:

  # Constructs graph representing real network

  G = read_pajek(file)

  # Prints basic statistics of real network

  graph_info(G)

  # Prints basic statistics of community structure of real network

  comms = clusters_info(G, lambda G: algorithms.girvan_newman(G, level = 1), 'betweenness')
  comms = clusters_info(G, algorithms.label_propagation, 'LPA') # fast algorithm
  comms = clusters_info(G, algorithms.louvain, 'Louvain') # modularity optimization
  comms = clusters_info(G, algorithms.infomap, 'Infomap') # network dynamics
  # comms = clusters_info(G, algorithms.sbm_dl, 'SBM') # arbitrary clusters

  # Visualizes community structure with wiring diagram

  viz.plot_network_clusters(G, partition = comms, position = nx.spring_layout(G), plot_labels = True)
  plt.show()

  # Visualizes community structure with block model

  plot_block_model(G, comms)
  plt.show()

#
# Larger networks with labels associated with nodes
#

for file in ['got-appearance', 'diseasome', 'wars', 'ingredients']:

  # Constructs graph representing real network

  G = read_pajek(file)

  # Prints basic statistics of real network

  graph_info(G)

  # Finds community structure of real network

  comms = clusters_info(G, algorithms.label_propagation, 'LPA') # fast algorithm
  comms = clusters_info(G, algorithms.leiden, 'Leiden') # modularity optimization
  comms = clusters_info(G, algorithms.infomap, 'Infomap') # network dynamics
  # comms = clusters_info(G, algorithms.sbm_dl, 'SBM', 10) # arbitrary clusters

  # Visualizes community structure with wiring diagram

  if len(G) < 1000:
    viz.plot_network_clusters(G, partition = comms, position = nx.spring_layout(G), node_size = 100, plot_labels = True)
    plt.show()

  # Visualizes community structure with block model

  if len(G) < 1000:
    plot_block_model(G, comms)
    plt.show()

  # Prints out largest community of real network

  print(sorted(comms.communities, key = len, reverse = True)[0])
  print()

#
# Random graphs with no mesoscopic structure
#

for k in range(5, 25, 5):

  # Constructs Erdös-Rényi random graph

  n = 10000
  G = nx.gnm_random_graph(n, n * k / 2)
  G.name = 'Erdös-Rényi'

  for c, C in enumerate(nx.connected_components(G)):
    for i in C:
      G.nodes[i]['cluster'] = c

  # Prints out statistics of random graph

  graph_info(G)

  # Finds community structure of random graph

  comms = clusters_info(G, algorithms.label_propagation, 'LPA', 10) # fast algorithm
  comms = clusters_info(G, algorithms.leiden, 'Leiden', 10) # modularity optimization
  comms = clusters_info(G, algorithms.infomap, 'Infomap', 10) # network dynamics
  # comms = clusters_info(G, algorithms.sbm_dl, 'SBM', 1) # arbitrary clusters

#
# k-cores decomposition of real networks
#

def k_core(G, k):
  """
  Find k-core of undirected multigraph G.
  """
  
  change = True
  while change:
    change = False
    
    for i in list(G.nodes()):
      if G.degree(i) < k:
        G.remove_node(i)
        change = True
        
  return G
  
def k_main(G):
  """
  Find main k(-core) of undirected multigraph G.
  """

  k = 0
  K = nx.MultiGraph(G)

  while K:
    K = k_core(K, k)

    if len(K) == 0:
      return k - 1
    k += 1

  return k
 
for file in ['got-appearance', 'diseasome', 'wars', 'ingredients']:

  # Constructs graph representing real network

  G = read_pajek(file)

  # Prints basic statistics of real network

  graph_info(G)

  # Finds main k-core of real network

  print("{:>15s} | '{:s}'".format('Graph', G.name))

  k = k_main(G)
  K = k_core(G, k)
  # K = nx.k_core(nx.Graph(G))
  K.name = str(k) + '-core'

  print("{:>15s} | {:,d}\n".format(K.name, len(K)))

  # Prints main k-core of real network

  print(K.nodes())
  print()
