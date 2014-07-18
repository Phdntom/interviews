from __future__ import division, print_function

import networkx as nx
import sys
import matplotlib.pyplot as plt

def load_nodes(node_file):
    '''
    '''
    node_list = []
    with open(node_file,"r") as f:
        node_header = f.readline()
        node_contents = f.readlines()
        for node_line in node_contents:
            node_id, name = node_line.strip().split("\t")
            entry = (int(node_id), name)
            node_list.append(entry)
    return node_list

def load_edges(edge_file):
    '''
    '''
    edge_list = []
    with open(edge_file,"r") as f:
        edge_header = f.readline()
        edge_contents = f.readlines()
        for edge_line in edge_contents:
            source, target, weight = edge_line.strip().split("\t")
            entry = int(source), int(target), float(weight)
            edge_list.append(entry)
    return edge_list

def build_graph(node_list, edge_list):
    '''
    '''
    G = nx.Graph()
    for node_id, name in node_list:
        G.add_node(node_id, name=name)
    
    for src, tar, weight in edge_list:
        G.add_edge(src, tar, weight=weight, distance=1/weight)
        
    return G

def weighted_eccentricity(G, v=None, sp=None, weight='distance'):
    '''
    Parameters
    ----------
    G           networkx graph
    v           a valid node in G
    sp          a networkx shortest path
    weight      the edge attribute to use for weighting edges in G

    Returns
    -------
    e           dictionary of eccentricity keyed by nodes in G
    if v specified
    e[v]        a single eccentricity of node v in graph G
    '''
    e={}
    for n in G.nbunch_iter(v):
        if sp is None:
            length=nx.single_source_dijkstra_path_length(G,n,weight=weight)
            L = len(length)
        else:
            try:
                length=sp[n]
                L = len(length)
            except TypeError:
                raise nx.NetworkXError('Format of "sp" is invalid.')
        #if L != order:
        #    msg = "Graph not connected: infinite path length"
        #    raise networkx.NetworkXError(msg)
            
        e[n]=max(length.values())

    if v in G:
        return e[v]  # return single value
    else:
        return e

def short_name(name,width=30):
    '''
    Parameters
    ----------
    name:       str of arbitrary length

    Return
    ------
    name:       str ready to be printed in width space format
    '''
    if len(name) > width:
        return name[:width-3] + "..."
    else:
        return name

def explain_G(G, node_id):
    parent_node = G.node[node_id]['name']
    print("{0} is connected to these topics:\n".format(parent_node))
    print("\t{0:25}\t{1:10}".format('Field','Relatedness'))
    for n in G[node_id]:
        name = G.node[n]['name']
        if len(name) > 25:
            name = name[:22] + "..."
        weight = G[node_id][n]['weight']
        print("\t  {0:25}\t{1:10}".format(name,weight))

if __name__ == "__main__":
    node_file = "academia-ri-nodes.txt"
    edge_file = "academia-ri-edges.txt"

    node_list = load_nodes(node_file)
    edge_list = load_edges(edge_file)
    
    G = build_graph(node_list, edge_list)

    # Sort the name_degrees list descending by the degree
    # Output top 10 Research interests
    name_degrees = []
    for node in G.nodes_iter():
        name = G.node[node]['name']
        degree = G.degree(node)
        name_degrees.append( (name,degree) )

    name_degrees.sort(key=lambda t: t[1], reverse=True)
    print("The top 10 Research Interests by simple degree:\n")
    for name, deg in name_degrees[:10]:
        print("  {0:25}\t{1:2d}".format(name,deg))

    # Run Page Rank and output top 10 Research Interests
    # Note that this works even if G is not connected
    page_rank = nx.pagerank(G)
    rank_list = []
    for node in page_rank:
        rank_list.append( (node, page_rank[node], G.node[node]['name']) )
    rank_list.sort(key=lambda t: t[1], reverse=True)

    print("The top 10 Research Interests by Page rank:\n")
    for node, deg, name in rank_list[:10]:
        print("  {0:25}\t{1:2.2%}".format(name,deg))

    # The graph is disconnected so unrelatedness is potentially infinite
    # 
    N_con_comp = nx.number_connected_components(G)
    print("\nThe number of connected components is ", N_con_comp)
    # We can analyze each Subgraph S
    print("\nAnalyzing each connected component...\n")
    print("Relatedness and Unrelatedness are defined via the")
    print("weighted global eccentricity. Small eccentricity")
    print("means the topic is more related to all subjects.")
    print("Large eccentricity means that the topic is less")
    print("related to all subjects. NOTE: For unrelatedness")
    print("some items have eccenctricty=infinity, since they")
    print("are in different connected components. The numbers")
    print("reported are therefore within a given component.\n")

    print("Any connected component with order less than 5 is not shown.\n")
    stored_ecc = []
    for S in nx.connected_component_subgraphs(G):
        order = S.order()
        if order < 5:
            continue
        print("This component is of order = ", order)
        print("{0:30}{1:10}".format('Research Interest',"Eccentricity"))
        weighted_ecc = weighted_eccentricity(S)
        ecc_list = []
        for key in weighted_ecc:
            ecc_list.append( (S.node[key]['name'], weighted_ecc[key]) )
        ecc_list.sort(key=lambda t: t[1], reverse=True)
        stored_ecc.append(ecc_list)
        for name, val in ecc_list[:5]:
            print("  {0:30}{1:2.2f}".format(short_name(name),val))
        print("    ...")
        for name, val in ecc_list[-5:]:
            print("  {0:30}{1:2.2f}".format(short_name(name),val))
        print()

    for each in stored_ecc:
        if len(each) < 20:
            continue
        array = [c[1] for c in each]
        fig, ax = plt.subplots()
        ax.hist(array, bins=20)
        ax.set_xlabel("eccentricity")
        ax.set_title("Measure of unrelatedness of Research Topics")
        fname = "histogram_"+str(len(each))+".pdf"
        plt.savefig(fname)
        

