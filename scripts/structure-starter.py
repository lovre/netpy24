import os
from time import *
from random import sample

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

def graph_info(G):
  """
  Print basic statistics of undirected multigraph G.
  """
  
  tic = time()
  
  print("{:>15s} | '{:s}'".format('Graph', G.name))
  
  n = len(G)
  m = G.number_of_edges()
  
  print("{:>15s} | {:,d}".format('Nodes', n))
  print("{:>15s} | {:,d}".format('Edges', m))
  
  print("{:>15s} | {:.1f} sec\n".format('Time', time() - tic))

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

# Pajek files: 'karate', 'women', 'dolphins', 'ingredients', 'darknet', 'ppi', 'internet', 'amazon', 'aps', 'google', 'texas'

# Useful functions: nx.number_of_isolates, nx.number_of_selfloops, nx.connected_components, nx.average_clustering, nx.gnm_random_graph etc.
