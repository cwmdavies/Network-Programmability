import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_excel(r'CDP_Neighbors_Detail.xlsx')

G = nx.from_pandas_edgelist(df, 'LOCAL_HOST', 'DESTINATION_HOST')
nx.draw_planar(G, with_labels=True, node_color="skyblue", node_shape="o", alpha=0.5, linewidths=4, font_color="grey",
               font_weight="bold", width=2, edge_color="grey", horizontalalignment="left", verticalalignment="top")

plt.show()
