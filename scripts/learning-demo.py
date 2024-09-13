import os

import networkx as nx

from cdlib import algorithms
from node2vec import Node2Vec

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
        G.add_node(node[1], _class = int(node[2]) if len(node[2]) > 0 else 0)
        
    for line in file:
      edge = line.strip().split(' ')
      G.add_edge(nodes[edge[0]], nodes[edge[1]])
      
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

for name in ['karate', 'sicris', 'directors', 'java']:

  # Constructs simple graph representing real network

  G = read_pajek(name)
  G = nx.Graph(G)

  # Prints basic statistics of real network

  graph_info(G)

  # Computes node centralities of real network

  DC = nx.degree_centrality(G)
  PR = nx.pagerank(G)
  
  C = nx.clustering(G)
  
  CC = nx.closeness_centrality(G)
  BC = nx.betweenness_centrality(G)

  # Finds community structure of real network

  leiden = {}
  for c, comm in enumerate(algorithms.leiden(G).communities):
    for i in comm:
      leiden[i] = c
      
  infomap = {}
  for c, comm in enumerate(algorithms.infomap(G).communities):
    for i in comm:
      infomap[i] = c

  # Writes node features to tab-separated file

  with open('../nets/' + name + '-features.tab', 'w') as file:
    file.write("m#node\tC#degree\tC#pagerank\tC#clustering\tC#closeness\tC#betweenness\tD#leiden\tD#infomap\tcD#class\n")
    for node in G.nodes(data = True):
      i, c = node[0], node[1]['_class']
      file.write("{:s}\t{:f}\t{:f}\t{:f}\t{:f}\t{:f}\t{:d}\t{:d}\t{:d}\n".format(i, DC[i], PR[i], C[i], CC[i], BC[i], leiden[i], infomap[i], c))
  
  # Computes node embeddings using node2vec

  dims = 32
  n2v = Node2Vec(G, dimensions = dims, p = 1, q = 1, workers = 8, quiet = True).fit().wv
  
  # Writes node embeddings to tab-separated file

  with open('../nets/' + name + '-node2vec.tab', 'w') as file:
    file.write("m#node\t" + "\t".join(["C#node2vec-" + str(i) for i in range(dims)]) + "\tcD#class\n")
    for node in G.nodes(data = True):
      i, c = node[0], node[1]['_class']
      file.write(i + "\t" + "\t".join([str(x) for x in n2v[i]]) + "\t" + str(c) + "\n")
