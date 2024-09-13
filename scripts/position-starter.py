import os
from time import *

import networkx as nx

def read_pajek(file, path = '../nets'):
  """
  Read (un)directed multigraph from Pajek file.
  """

  G = nx.read_pajek(os.path.join(path, file + '.net'))
  G.name = file
  
  return G

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
  
def top_nodes(G, centrality, label, n = 15):
  """
  Print highest centrality nodes of (un)directed multigraph G.
  """
  
  print("{:>15s} | '{:s}'".format('Graph', G.name))
  print("{:>15s} | '{:s}'".format('Centrality', label))
  
  for p, (i, c) in enumerate(sorted(centrality.items(), key = lambda item: (-item[1], -G.degree(item[0]), item[0]))):
    if p >= n:
      break
    print("{:>15.8f} | '{:s}' ({:,d})".format(c, i, G.degree(i)))
  print()

# Constructs multigraph representing IMDb network
  
G = read_pajek('imdb')
  
# Prints basic statistics of IMDb network
  
graph_info(G)
  
# Prints top degree centrality nodes of IMDb network

top_nodes(G, nx.degree_centrality(G), 'degree')

# Pajek files: 'got-kills', 'lpp', 'ingredients', 'imdb'

# Useful functions: nx.clustering, nx.eigenvector_centrality, nx.pagerank, nx.closeness_centrality, nx.betweenness_centrality
