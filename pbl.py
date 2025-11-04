import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import itertools

# Page Config
st.set_page_config(page_title="💉 Vaccination Center Planner", layout="wide")

# Styling (Light Modern)
st.markdown("""
    <style>
        body {
            background-color: #f8fafc;
            color: #2c3e50;
        }
        .main-title {
            text-align: center;
            color: #2c3e50;
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .subtext {
            text-align: center;
            color: #7f8c8d;
            font-size: 16px;
            margin-bottom: 30px;
        }
        .metric-container {
            display: flex;
            justify-content: center;
            gap: 25px;
            margin-top: 25px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        .metric-card {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(8px);
            border-radius: 15px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
            padding: 25px;
            text-align: center;
            width: 240px;
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0px 8px 20px rgba(0,0,0,0.12);
        }
        .metric-title {
            font-size: 16px;
            color: #5d6d7e;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #2c3e50;
        }
        .metric-highlight {
            color: #3498db;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>💉 Vaccination Center Planner</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtext'>Optimize vaccination center placement based on population and coverage distance</p>", unsafe_allow_html=True)

# Helper Functions
def covered_nodes(G, center, X):
    """Return all nodes within distance X from a given center."""
    return {node for node, dist in nx.single_source_shortest_path_length(G, center).items() if dist <= X}

def greedy_center_placement(G, X):
    """Greedy algorithm for optimal center placement."""
    uncovered = set(G.nodes())
    centers = []
    while uncovered:
        best_node, best_cover = None, set()
        for node in G.nodes():
            cover = covered_nodes(G, node, X) & uncovered
            if len(cover) > len(best_cover):
                best_node, best_cover = node, cover
        centers.append(best_node)
        uncovered -= best_cover
    return centers

# Sidebar Inputs
st.sidebar.header("⚙️ Settings")

num_locations = st.sidebar.number_input("Number of Locations", min_value=2, value=10, step=1)
population_input = st.sidebar.text_area(
    f"Population at each location (comma-separated, {num_locations} values)",
    value=",".join(["10"] * num_locations)
)
X = st.sidebar.slider("Coverage Distance (X)", min_value=1, max_value=5, value=2)
st.sidebar.markdown("---")
st.sidebar.info("🟥 = Centers | 🟩 = Covered | 🔵 = Uncovered")

# Compute Button
if st.sidebar.button("Compute Centers"):
    try:
        population_list = list(map(int, population_input.split(",")))
        if len(population_list) != num_locations:
            st.error(f"Please enter exactly {num_locations} population values.")
        else:
            # Build Graph (chain layout)
            G = nx.Graph()
            for i in range(1, num_locations + 1):
                G.add_node(i, population=population_list[i-1])
            for i in range(1, num_locations):
                G.add_edge(i, i + 1)

            # Apply Algorithm
            centers = greedy_center_placement(G, X)

            # Determine coverage groups
            center_coverage_map = {}
            all_covered = set()
            for c in centers:
                nodes_covered_by_c = covered_nodes(G, c, X)
                center_coverage_map[c] = sorted(list(nodes_covered_by_c))
                all_covered |= nodes_covered_by_c

            uncovered = set(G.nodes()) - all_covered

            # Compute Stats
            total_population = sum(population_list)
            covered_population = sum(G.nodes[n]['population'] for n in all_covered)
            coverage_percent = (covered_population / total_population) * 100

            
            # Coverage Summary
           
            st.markdown("### 📊 Coverage Summary")
            st.markdown(f"""
                <div class='metric-container'>
                    <div class='metric-card'>
                        <div class='metric-title'>Total Locations</div>
                        <div class='metric-value metric-highlight'>{num_locations}</div>
                    </div>
                    <div class='metric-card'>
                        <div class='metric-title'>Centers Placed</div>
                        <div class='metric-value metric-highlight'>{len(centers)}</div>
                    </div>
                    <div class='metric-card'>
                        <div class='metric-title'>Population Covered</div>
                        <div class='metric-value metric-highlight'>{coverage_percent:.1f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"### 📍 Centers placed at: `{centers}`")

           
            # Display coverage for each center
            
            st.markdown("### 🧭 Node Coverage by Each Center")
            for c in centers:
                st.write(f"🟥 **Center {c}** covers nodes: {center_coverage_map[c]}")

           
            # Visualization (Color by Center)
           
            st.markdown("### 🗺️ Visual Representation")

            plt.figure(figsize=(10, 6))
            pos = nx.circular_layout(G)

            min_pop, max_pop = min(population_list), max(population_list)
            node_sizes = [
                600 + ((G.nodes[n]['population'] - min_pop) / (max_pop - min_pop + 1)) * 1200
                for n in G.nodes()
            ]

            # Generate distinct colors for centers
            color_palette = ["#e74c3c", "#27ae60", "#9b59b6", "#f39c12", "#16a085", "#d35400", "#2980b9"]
            color_cycle = itertools.cycle(color_palette)

            node_colors = {}
            center_colors = {}

            # Assign same color for center and its covered nodes
            for c in centers:
                color = next(color_cycle)
                center_colors[c] = color
                for node in center_coverage_map[c]:
                    node_colors[node] = color

            # Assign blue for uncovered nodes
            for node in uncovered:
                node_colors[node] = "#3498db"

            nx.draw_networkx_edges(G, pos, width=2, alpha=0.3, edge_color="#95a5a6")

            nx.draw_networkx_nodes(
                G,
                pos,
                node_color=[node_colors[n] for n in G.nodes()],
                node_size=node_sizes,
                alpha=0.9,
                edgecolors="black",
                linewidths=1.2
            )

            labels = {i: f"{i}\n({G.nodes[i]['population']})" for i in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_color="#2c3e50")

            # Draw circle and label for each center
            for c in centers:
                cx, cy = pos[c]
                circle = plt.Circle((cx, cy), 0.25 * X, color=center_colors[c], alpha=0.2, zorder=0)
                plt.gca().add_patch(circle)
                plt.text(cx, cy + 0.25 * X + 0.03, f"Center {c}", ha='center', fontsize=9, color=center_colors[c])

            plt.title(f"Vaccination Center Placement (Coverage Distance = {X})",
                      fontsize=15, fontweight='bold', color="#2c3e50")
            plt.axis("off")
            plt.tight_layout()
            st.pyplot(plt)

            
            # Algorithm Explanation
           
            with st.expander("📘 Algorithm & Explanation"):
                st.markdown("""
                **Algorithm Used:** Greedy Center Placement  
                ---
                **Step-by-Step Process:**
                1. Start with all locations uncovered.  
                2. For each node, calculate how many uncovered locations can be covered within distance **X**.  
                3. Select the node covering the most uncovered nodes and mark it as a **center**.  
                4. Mark all its reachable nodes within distance **X** as **covered**.  
                5. Repeat until every node is covered.  

                ---
                **Why Greedy Algorithm?**
                - Simple, efficient, and provides near-optimal coverage.  
                - Perfect for resource allocation problems like vaccination, hospitals, or ATM placement.  

                ---
                **Visualization Key:**
                - 🟥 = Vaccination Centers  
                - 🟩 = Covered Locations  
                - 🔵 = Uncovered Locations  

                ---
                **Observation:**
                - Increasing Coverage Distance (**X**) reduces the number of centers needed.  
                - Population size affects node size (larger = bigger node).  
                """)
    except Exception as e:
        st.error(f"⚠️ Invalid input! Please enter comma-separated integers. Error: {e}")
