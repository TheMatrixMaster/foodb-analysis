import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from utils import *

# Load the data
foods = pd.read_csv('data/Food.csv', header=0, index_col=0)
compounds = pd.read_csv('data/Compound.csv', header=0, index_col=0)
content = pd.read_csv('data/Content.csv', header=0, index_col=0)

# Run some statistics over foods and compounds
content = content[content['source_type'] == 'Compound']
content = content[content['source_id'].isin(compounds.index)]
content = content[content['food_id'].isin(foods.index)]

# Content file reports all occurrences of a compound in a food by many organization, so we need to remove duplicates
report_count = content.groupby(['food_id', 'source_id']).size().rename('report_count')
content.drop_duplicates(subset=['food_id', 'source_id'], inplace=True)
content = content.merge(report_count, left_on=['food_id', 'source_id'], right_index=True)

# Add the number of compounds and foods to the foods and compounds dataframes
foods = foods.merge(content.groupby('food_id').size().rename('num_compounds'), left_index=True, right_index=True)
compounds = compounds.merge(content.groupby('source_id').size().rename('num_foods'), left_index=True, right_index=True)

print("the maximum number of compounds in one food is: ", foods['num_compounds'].max())
print("the maximum number of foods per compound is: ", compounds['num_foods'].max())
print()

# Only keep the top 50% of compounds by number of foods they are in
print(foods['num_compounds'].describe())
print(compounds['num_foods'].describe())

compounds.sort_values(by=['num_foods'], ascending=False, inplace=True)
outliers = compounds[compounds['num_foods'] > compounds['num_foods'].quantile(0.99)]

# Create the weighted edgelist where the weight between two foods is equal to the number of compounds they share
edgelist = []
food_idx = foods.index

for i in tqdm(range(len(food_idx))):
    for j in tqdm(range(i+1, len(food_idx))):
        food1 = food_idx[i]
        food2 = food_idx[j]
        
        # Get the compounds that are in both foods
        cur_comp = content[content['food_id'].isin([food1, food2])]['source_id']
        cur_comp = cur_comp[cur_comp.duplicated(keep=False)] \
                    .drop_duplicates().reset_index(drop=True)

        # To normalize the edge weight, we will scale back the weight of each compound by the number of foods it is in
        weight = sum([1/compounds.loc[c, 'num_foods'] for c in cur_comp.values])

        # Add weight to the edgelist
        edgelist.append((food1, food2, {'weight': weight}))


# Plot the histogram of edge weights
plt.hist([v['weight'] for _, _, v in edgelist], bins=100)
plt.show()

# # Create a graph

# g_nodes = foods.to_dict('index')
# # g_edges = 

# g = nx.Graph()
# g.add_nodes_from(g_nodes)
# g.add_edges_from()

# print(len(g.nodes))
# print(len(g.edges))