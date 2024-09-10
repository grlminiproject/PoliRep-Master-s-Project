import argparse
import os
import sys

import networkx as nx
import matplotlib.pyplot as plt

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.polirep.polirep_generator import get_polirep_per_policy


def visualize_polirep(policy_path, model, output_dir="./output"):
    _, entities, relations = get_polirep_per_policy(policy_path, model)


    # Create a new graph
    G = nx.Graph()

    # Add nodes
    for category, entity_set in entities.items():
        for item in entity_set:
            if isinstance(item, tuple):
                entity, _ = item
            else:
                entity = item
            G.add_node(entity, category=category)

    # Add edges
    for relation_type, relation_pairs in relations.items():
        for source, target in relation_pairs:
            G.add_edge(source, target, relation=relation_type)

    # Set up the plot
    plt.figure(figsize=(16, 12))

    # Define node colors based on categories
    color_map = {'data': 'skyblue', 'purpose': 'lightgreen', 'third-party': 'lightcoral', 'protection-method': 'yellow'}
    node_colors = [color_map.get(G.nodes[node]['category'], 'gray') for node in G.nodes()]

    # Define edge colors based on relation types
    edge_color_map = {'purpose': 'green', 'disclosure': 'red'}
    edge_colors = [edge_color_map.get(G.edges[edge]['relation'], 'blue') for edge in G.edges()]

    # Create layout
    pos = nx.spring_layout(G, k=0.5, iterations=50)

    # Draw the graph
    nx.draw(G, pos, node_color=node_colors, edge_color=edge_colors, with_labels=True,
            node_size=3000, font_size=6, font_weight='bold')

    # Add a legend for node categories
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=cat.capitalize(),
                                  markerfacecolor=color, markersize=10)
                       for cat, color in color_map.items()]
    plt.legend(handles=legend_elements, title="Node Categories", loc='upper left', bbox_to_anchor=(1, 1))

    # Add a legend for edge relations
    legend_elements = [plt.Line2D([0], [0], color=color, label=rel.capitalize())
                       for rel, color in edge_color_map.items()]
    plt.legend(handles=legend_elements, title="Edge Relations", loc='upper left', bbox_to_anchor=(1, 0.7))

    plt.title(f"Policy Representation Graph: {os.path.basename(policy_path)}")
    plt.tight_layout()

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate output filename
    output_filename = f"policy_graph_{os.path.basename(policy_path)}_{model}.png"
    output_path = os.path.join(output_dir, output_filename)

    # Save the plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close the plot to free up memory

    print(f"Graph saved to: {output_path}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize PoliRep for a given policy.")
    parser.add_argument("policy_path", help="Path to the policy folder")
    parser.add_argument("model", choices=["OpenAI", "Anthropic"], help="Model to use (OpenAI or Anthropic)")
    args = parser.parse_args()

    policy_path = "../../data/annotations/final_benchmark/9gag"
    model = "OpenAI"
    # visualize_polirep(policy_path, model)

    visualize_polirep(args.policy_path, args.model)


    # visualize_polirep_test(output_dir="./test_output")
    # visualize_small_graph(output_dir="./test_output")
