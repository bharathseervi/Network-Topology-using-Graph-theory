import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from networkx.algorithms import approximation as approx

# Page Setup
st.set_page_config(page_title="Network Architect Pro", layout="wide")

# --- SESSION STATE ---
if 'nodes' not in st.session_state:
    st.session_state.nodes = {}
if 'links' not in st.session_state:
    st.session_state.links = []

st.title("🛡️ Network Architecture & Graph Theory Intelligence")
st.markdown("Build your physical link infrastructure and generate a full diagnostic report.")

# --- SIDEBAR: CONSTRUCTION ---
with st.sidebar:
    st.header("🛠️ Infrastructure Builder")
    with st.form("node_input"):
        n_id = st.text_input("Device Name", "PC-01")
        n_type = st.selectbox("Device Type", ["PC", "Router", "Switch"])
        if st.form_submit_button("Add Device"):
            st.session_state.nodes[n_id] = n_type
            st.rerun()

    st.header("🔗 Physical Link Setup")
    if len(st.session_state.nodes) >= 2:
        with st.form("link_input"):
            src = st.selectbox("Device A", list(st.session_state.nodes.keys()))
            dst = st.selectbox("Device B", list(st.session_state.nodes.keys()))
            weight = st.number_input("Link Weight (Latency/KM)", min_value=1, value=10)
            if st.form_submit_button("Establish Link"):
                if src != dst:
                    st.session_state.links.append({'u': src, 'v': dst, 'w': weight})
                    st.rerun()

    if st.sidebar.button("🗑️ Reset All Data"):
        st.session_state.nodes, st.session_state.links = {}, []
        st.rerun()

# --- MAIN WORKSPACE ---
if not st.session_state.nodes:
    st.info("👈 Use the sidebar to add hardware devices and establish links.")
else:
    # Build Graph Objects
    G = nx.Graph() # Physical Undirected Graph
    G_dir = nx.DiGraph() # Used for Flow/Degree Analysis
    
    for n, t in st.session_state.nodes.items():
        G.add_node(n, type=t)
        G_dir.add_node(n, type=t)
    for link in st.session_state.links:
        G.add_edge(link['u'], link['v'], weight=link['w'])
        G_dir.add_edge(link['u'], link['v'], weight=link['w'])

    # 1. ADJUSTABLE VISUALIZATION
    st.subheader("🖼️ Adjustable Network Map")
    col_ctrl, col_viz = st.columns([1, 3])
    
    with col_ctrl:
        st.write("**Visual Tuning**")
        spread = st.slider("Node Spacing", 0.5, 5.0, 2.0)
        node_size = st.slider("Node Icon Size", 500, 3000, 1500)
        
    with col_viz:
        fig, ax = plt.subplots(figsize=(10, 6))
        pos = nx.spring_layout(G, k=spread/len(G.nodes)**0.5)
        
        colors = {"PC": "#2ecc71", "Router": "#e74c3c", "Switch": "#f1c40f"}
        n_colors = [colors[st.session_state.nodes[n]] for n in G.nodes()]
        
        nx.draw(G, pos, with_labels=True, node_color=n_colors, 
                node_size=node_size, font_weight='bold', edge_color='#7f8c8d', width=2)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
        st.pyplot(fig)
        st.caption("🟢 PC | 🔴 Router | 🟡 Switch")

    # 2. SHORTEST PATH ROUTING
    st.divider()
    st.subheader("🛤️ Shortest Path Routing")
    r1, r2 = st.columns(2)
    with r1: start_node = st.selectbox("Source Device", list(G.nodes()), key="s")
    with r2: end_node = st.selectbox("Target Device", list(G.nodes()), key="e")
    
    if st.button("Calculate Optimal Route"):
        try:
            path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')
            dist = nx.shortest_path_length(G, source=start_node, target=end_node, weight='weight')
            st.success(f"**Path Found:** {' ➔ '.join(path)}")
            st.info(f"**Total Path Cost (Minimal Distance/Latency):** {dist}")
        except:
            st.error("No link path exists between these devices.")

    # 3. COMPREHENSIVE INTELLIGENCE REPORT
    if st.button("📄 GENERATE FULL INTELLIGENCE REPORT", type="primary"):
        st.divider()
        
        # --- TOPOLOGY & JUSTIFICATION ---
        st.header("1. Topology & Graph Classification")
        n, e = G.number_of_nodes(), G.number_of_edges()
        degrees = dict(G.degree())
        max_deg = max(degrees.values()) if degrees else 0
        
        topo, justify = "Hybrid / Custom", "The connection pattern is irregular and does not follow a fixed geometric model."
        
        # Topology Logic
        if any(t == "Switch" for t in st.session_state.nodes.values()) and max_deg == n-1:
            topo, justify = "Star Topology", f"Justification: A central Hub (Switch) connects to all other nodes. Center degree = {max_deg} (N-1)."
        elif n >= 3 and all(d == 2 for d in degrees.values()):
            topo, justify = "Ring Topology", "Justification: Every node has exactly 2 connections, forming a closed cycle with no endpoints."
        elif e == (n * (n - 1) / 2):
            topo, justify = "Full Mesh Topology", f"Justification: Every node is directly linked to all others. Total links {e} = N(N-1)/2."

        

        c1, c2 = st.columns(2)
        c1.success(f"**Topology Type:** {topo}")
        c2.info(f"**Justification:** {justify}")

        # --- DEGREE ANALYSIS & JUSTIFICATION ---
        st.header("2. Degree Calculations & Flow Logic")
        st.markdown("Mathematical justification of node importance based on undirected and directed flow.")
        
        

        degree_records = []
        for node in G.nodes():
            in_d = G_dir.in_degree(node)
            out_d = G_dir.out_degree(node)
            total_d = G.degree(node)
            degree_records.append({
                "Device": node,
                "Type": st.session_state.nodes[node],
                "In-Degree": in_d,
                "Out-Degree": out_d,
                "Justification": f"Σ(In={in_d}) + Σ(Out={out_d}) = Total Degree {total_d}"
            })
        st.table(pd.DataFrame(degree_records))

        # --- TRAVELING SALESMAN PROBLEM ---
        st.header("3. Traveling Salesman Problem (TSP)")
        
        if n >= 3:
            try:
                tsp_path = approx.traveling_salesperson_problem(G, cycle=True)
                path_weight = sum(G[u][v]['weight'] for u, v in zip(tsp_path[:-1], tsp_path[1:]))
                
                st.warning(f"**Minimum Traveling Route:** {' ➔ '.join(tsp_path)}")
                st.write(f"**Justification:** This route visits all {n} hardware devices and returns to the origin with the lowest mathematical cost of **{path_weight}**.")
            except:
                st.error("TSP Error: The graph must be fully connected (all nodes reachable).")
        else:
            st.warning("Need at least 3 nodes for TSP analysis.")