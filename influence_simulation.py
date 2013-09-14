#!/usr/bin/env python
"""
The simulator for influence graph, from the original networkx graph in Polly. 
Yibin Lin Jul. 2013
"""
import networkx as nx
import csv
import sys
import os
import math
import random
import numpy as np
import optparse
import datetime
from collections import defaultdict

def create_graph(file_name, separater, reverse=False):
    """
    Create a graph from a csv file, starting from 0.
    """
    DG=nx.DiGraph()
    with open(file_name, 'rb') as f:
            mycsv = csv.reader(f, delimiter=separater)
            cnt = 0
            for row in mycsv:
                cnt += 1
                if not reverse:
                    DG.add_edge(int(row[0]), int(row[1]))
                else:
                    DG.add_edge(int(row[1]), int(row[0]))
                if cnt % 10000 == 0:
                    sys.stderr.write(".")
    sys.stderr.write("\n")
    return DG

def create_multi_graph(file_name, separater, weights=False, reverse=False):
    """
    Create a graph from a csv file, starting from 0, using nx.MultiDiGraph
    weights: contain weights in the thrid column
    """
    DG=nx.MultiDiGraph()
    with open(file_name, 'rb') as f:
            mycsv = csv.reader(f, delimiter=separater)
            cnt = 0
            for row in mycsv:
                cnt += 1
                from_number = int(row[0])
                to_number = int(row[1])
                if weights:
                    weight = int(row[2])
                
                if not reverse:
                    if not weights:
                        DG.add_edge(from_number, to_number)
                    else:
                        for i in xrange(weight):
                            DG.add_edge(from_number, to_number)
                else:
                    DG.add_edge(to_number, from_number)

                if cnt % 10000 == 0:
                    sys.stderr.write(".")
    sys.stderr.write("\n")
    return DG

def create_weighted_graph(file_name, separater, reverse=False):
    """
    create a graph, weight as attributes. 
    """
    G = nx.DiGraph()
    with open(file_name, 'rb') as f:
            mycsv = csv.reader(f, delimiter=separater)
            cnt = 0
            for row in mycsv:
                cnt += 1
                from_id = int(row[0])
                to_id = int(row[1])
                weight = int(row[2])
                if not reverse:
                    G.add_edge(from_id, to_id, w=weight)
                else:
                    G.add_edge(to_id, from_id, w=weight)
                if cnt % 10000 == 0:
                    sys.stderr.write(".")
    sys.stderr.write("\n")
    return G

def exponential_decay(days, alpha=1.5, P0=0.5):
    """
    Exponential dacay of excitements, default 1.5 by paper Barabasi, et al. 
    """
    Pt = (P0 * math.pow((1.0 * days), (-1.0 * alpha)))
#    print Pt
    return Pt

def calcDynamicP0(G, node):
    """
    Dynamically calculate an initial probability of a node notifying her friends for a node in G according to the weight of her in the base network G
    It is calculated by the following formula:
    P_{node, 0} = 1- frac{4}{N_f}
    """
    weight = sum([G[node][x]['w'] for x in G[node]]) / 4.0
    return (1.0 - 1.0/weight) if weight != 0.0 else 0.9
    

def simulate_influence_graph(G, day=100, seed_num_fr=5, P0=0.9, alpha=1.2):
    """
    simulate an influence graph from a friendship graph.
    G: the base network (underlying social network), weight designated in "w" attribute.
    P0: a value < 0.0 means it contains variable P0, according to how much weight a node has. In normal case, P0 \in [0.0, 1.0). 
    day: number of days to simulate. 
    returns: a MultiDiGraph influence graph
    TBD1: maybe a person who has been notified multiple times should have a new (higher) probability to be excited.. ?? 
    TBD2: the probability of the first five people
    """
    print ("simulation days: %d, P0=%f, alpha=%f." % (day, P0, alpha))
    t = 1
    """
    The dictionary for the infected nodes, e.g:
    {31: {'t': 15}, ...} t is infected time
    """
    first_infected = []
    infected = {} 
    influence_G = nx.MultiDiGraph() # the influence graph
    outgoing_days = defaultdict(defaultdict)

    """
    Initial infection of 5 people, the same as Polly.
    """
    population = len(G.nodes())
    for i in xrange(5):
        num_fr = 0
        node = 1
        while num_fr < seed_num_fr:
            node = G.nodes()[int(population * random.random())]
            if node in infected:
                continue
            num_fr = len(G[node])
        print "# of friends of the seed: %d." % len(G[node])
        infected[node] = {}
        infected[node]['t'] = 0
        infected[node]['P0'] = 0.9
        first_infected.append(node)
        
    print "random seeds: %s." % str(infected)

    while t <= day:
        new_users = 0

        for n in infected.keys():
            Pt = exponential_decay((t - infected[n]['t']), alpha=alpha, P0=infected[n]['P0']) 

            elapsed_days = (t - infected[n]['t'])
            
            while (Pt > 1e-8 and random.random() < Pt):
                total_weight = sum([G[n][x]['w'] for x in G[n]]) * 1.0
                friends = sorted(G[n].keys(), key=lambda x: G[n][x]['w'], reverse=True)
                weights = [G[n][x]['w'] for x in friends] 
                friend_order = -1

                pick = int((total_weight + 1) * random.random()) # the picked friend weight
                for i in xrange(len(weights)):
                    pick -= weights[i]
                    if pick <= 0:
                        friend_order = i
                        break
                if friend_order == -1:
                    if len(weights) != 0:
                        print "friend id not assigned!"
                        friend_order = len(weights) - 1
                    else:
                        continue

                friend_id = friends[friend_order] 
                if friend_id not in infected.keys():
                    infected[friend_id] = {}
                    infected[friend_id]['t'] = t
                    if P0 > 0.0:
                        infected[friend_id]['P0'] = P0
                    else:
                        infected[friend_id]['P0'] = calcDynamicP0(G, friend_id)
                    new_users += 1
                influence_G.add_edge(n, friend_id) # add one edge into the influence graph
                try:
                    outgoing_days[n][elapsed_days] += 1
                except KeyError:
                    outgoing_days[n][elapsed_days] = 1
        print "day: %d, # of new users: %d" % (t, new_users)

        t += 1
    return (influence_G, outgoing_days)


def write_graph(G, filename):
    """
    write all edges into a csv file.
    """
    f = open(filename, 'w')
    for (from_id, to_id) in G.edges():
        f.write("%d,%d,%d\n" % (from_id, to_id, G[from_id][to_id]['w']))
    f.close()
    return

def add_weight_from_multi_di_graph(DG):
    """
    returns a Digraph which has weights as the number of multiple edges between nodes. 
    """
    DWG = nx.DiGraph()
    for (from_n, to_n) in set(DG.edges()):
        DWG.add_edge(from_n, to_n, w=len(DG[from_n][to_n]))
    return DWG


def main():
    start_time = datetime.datetime.now()
    optparser = optparse.OptionParser()
    optparser.add_option("-d", "--days", dest="days", default=100, help="The csv edge file")
    optparser.add_option("-a", "--alpha", dest="alpha", default=1.17, help="The csv edge file")
    optparser.add_option("-p", "--pzero", dest="pzero", default=0.93, help="The csv edge file")

    (opts, _) = optparser.parse_args()

    friendship_graph = "enron_weighted.csv"

    print("Starting INFLOOD generator..\n")
    print("Loading the graph %s" % friendship_graph)
    
    """
    random Erdos-Renyi graph..
    """
    enron_multi = create_multi_graph(friendship_graph, ',', weights=True)

    """
    directed, weighted graph from Enron email graph.
    """
    enron = add_weight_from_multi_di_graph(enron_multi)

    (MDG, outgoing_days) = simulate_influence_graph(enron, day=int(opts.days), alpha=float(opts.alpha), P0=float(opts.pzero))
    print "# of nodes : %d." % (len(MDG.nodes()))
    print "total weight: %d." % (len(MDG.edges()))

    MDG_weight = add_weight_from_multi_di_graph(MDG)
    print "# of edges : %d." % (len(MDG_weight.edges()))

    stored_graph ="enron_influence_graph.csv" 
    write_graph(MDG_weight, stored_graph)
    print "influence graph stored in " + stored_graph + "\n"

    end_time = datetime.datetime.now()
    print "INFLOOD geneartor takes %d seconds.." % ((end_time-start_time).seconds)

    return
    

if __name__ == "__main__":
    """
    Announce main
    """
    main()
