import os
from time import *
from random import sample

import matplotlib.pyplot as plt

import networkx as nx

def read_pajek(file, path = '../nets'):
  """
  Read (un)directed multigraph from Pajek file.
  """
  
  tic = time()
  G = nx.read_pajek(os.path.join(path, file + '.net'))
  G.name = file
  
  return G, time() - tic

def approx_dists(G, n = 100):
  """
  Approximate average distance and diameter of undirected multigraph G.
  """
  
  ds = []
  for i in G.nodes() if len(G) <= n else sample(G.nodes(), n):
    ds.extend([d for d in nx.shortest_path_length(G, source = i).values() if d > 0])
    
  return sum(ds) / len(ds), max(ds)

def graph_info(G, cons_time = 0, fast = False):
  """
  Print basic statistics of undirected multigraph G.
  """
  
  tic = time()
  
  print("{:>15s} | '{:s}'".format('Graph', G.name))
  
  multi = False
  for edge in G.edges():
    if G.number_of_edges(edge[0], edge[1]) > 1:
      multi = True
      break
      
  print("{:>15s} | '{:s}'".format('Type', '===' if multi else '---'))
  
  n = len(G)
  n0 = nx.number_of_isolates(G)
  
  print("{:>15s} | {:,d} ({:,d})".format('Nodes', n, n0))
  
  m = G.number_of_edges()
  m0 = nx.number_of_selfloops(G)
  
  print("{:>15s} | {:,d} ({:,d})".format('Edges', m, m0))
  
  ks = [k for _, k in G.degree()]
  
  print("{:>15s} | {:.1f} ({:,d}, {:,d})".format('Degree', 2 * m / n, min(ks), max(ks)))
  print("{:>15s} | {:.8f}".format('Density', 2 * m / n / (n - 1)))
  
  if not fast:
    CCs = sorted(nx.connected_components(G), key = len, reverse = True)

    print("{:>15s} | {:.1f}% ({:,d})".format('Components', 100 * len(CCs[0]) / n, len(CCs)))

    d, D = approx_dists(G.subgraph(CCs[0]))

    print("{:>15s} | {:.3f} ({:,d})".format('Distances', d, D))

    C = nx.average_clustering(G if type(G) == nx.Graph else nx.Graph(G))

    print("{:>15s} | {:.6f}".format('Clustering', C))
  
  print("{:>15s} | {:.1f} sec".format('Construction', cons_time))
  print("{:>15s} | {:.1f} sec\n".format('Analysis', time() - tic))

def deg_dist(G):
  """
  Plot degree distribution of undirected multigraph G.
  """
  
  nk = {}
  for _, k in G.degree():
    if k not in nk:
      nk[k] = 0
    nk[k] += 1
  ks = list(nk)
  
  plt.loglog(ks, [nk[k] / len(G) for k in ks], '*k')
  plt.ylabel('Fraction of nodes $p_k$')
  plt.xlabel('Node degree $k$')
  plt.title(G.name)
  plt.show()

# Constructs small toy graph

G = nx.MultiGraph(name = 'toy')

G.add_node(1)
G.add_node(2)
G.add_node('foo', cluster = 1)
G.add_node('bar', value = 13.7)
G.add_node('baz')

G.add_edge(1, 2)
G.add_edge(1, 'foo')
G.add_edge(2, 'foo')
G.add_edge('foo', 'bar', weight = 2.0)

# Prints basic statistics of toy graph

graph_info(G)

for file in ['karate', 'women', 'dolphins', 'ingredients', 'darknet', 'ppi', 'internet', 'amazon', 'aps', 'google', 'texas']:

  # Constructs graph representing real network
  
  G, cons_time = read_pajek(file)
  
  # Prints basic statistics of real network
  
  n = len(G)
  m = G.number_of_edges()
  
  graph_info(G, cons_time, n > 400000)

  # Plots degree distribution of real network

  if n > 5000:
    deg_dist(G)

  if n < 400000:

    # Prints basic statistics of Erdös-Rényi random graph

    tic = time()
    ER = nx.gnm_random_graph(n, m)
    ER.name = 'Erdös-Rényi'

    graph_info(ER, time() - tic)

    # Prints basic statistics of Barabási–Albert scale-free graph

    tic = time()
    BA = nx.barabasi_albert_graph(n, round(m / n))
    BA.name = 'Barabási–Albert'

    graph_info(BA, time() - tic)
