from config import *

def plot_graph(G):
    plt.figure(figsize=(20,20))
    pos = nx.spring_layout(G)
    
    nx.draw_networkx_nodes(G, pos, node_size=700)
    nx.draw_networkx_labels(G, pos, labels=nx.get_node_attributes(G, 'label'), font_size=12)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrowstyle='-|>', arrowsize=20)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'label'))
    
    plt.show()

def create_and_plot_graph(entities, relations, filename="graph.png", output_dir="graphs"):
    G = nx.DiGraph()
    exist_entities = set([r['source'] for r in relations] + [r['target'] for r in relations])

    for e, v in entities.items():
        if e in exist_entities:
            G.add_node(e, label=e)

    for r in relations:
        G.add_edge(r['source'], r['target'], label=r['relation'], desc=r['desc'])

    plt.figure(figsize=(20, 20))
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=700)
    nx.draw_networkx_labels(G, pos, labels=nx.get_node_attributes(G, 'label'), font_size=12)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrowstyle='-|>', arrowsize=20)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'label'))

    filepath = os.path.join(output_dir, filename)
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(filepath)
    plt.close()