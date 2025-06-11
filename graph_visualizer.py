import networkx as nx
import matplotlib.pyplot as plt

def draw_flow_network(graph, source, sink, team_name):
    """
    Desenha o grafo de fluxo da rede de eliminação usando NetworkX e Matplotlib.
    """
    G = nx.DiGraph()

    # Adiciona as arestas com capacidade como rótulo
    for u in graph:
        for v in graph[u]:
            capacity = graph[u][v]
            G.add_edge(u, v, label=f"{capacity}")

    pos = nx.spring_layout(G, seed=42)  # Melhor visualização

    plt.figure(figsize=(12, 8))
    plt.gcf().canvas.manager.set_window_title(f"Rede de Fluxo - {team_name}")
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, arrows=True)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()
