import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from networkx.algorithms import approximation as approx

# ================= PAGE SETUP =================
st.set_page_config(
    page_title="Network Topology Analysis Using Graph Theory",
    layout="wide"
)

# ================= SESSION STATE =================
if "nodes" not in st.session_state:
    st.session_state.nodes = {}
if "links" not in st.session_state:
    st.session_state.links = []

# ================= TITLE =================
st.title("📡 Network Topology Analysis Using Graph Theory")
st.markdown(
    "Design and analyze **routing, OSPF, MST optimization, topology detection, "
    "and comparative justification** using **Graph Theory**."
)

# ================= SIDEBAR =================
with st.sidebar:
    st.header("🛠️ Infrastructure Builder")

    with st.form("node_form"):
        nid = st.text_input("Device Name", "R1")
        ntype = st.selectbox("Device Type", ["PC", "Switch", "Router"])
        if st.form_submit_button("Add Device"):
            st.session_state.nodes[nid] = ntype
            st.rerun()

    st.header("🔗 Link Setup")
    if len(st.session_state.nodes) >= 2:
        with st.form("link_form"):
            a = st.selectbox("Device A", list(st.session_state.nodes.keys()))
            b = st.selectbox("Device B", list(st.session_state.nodes.keys()))
            w = st.number_input("Link Cost", min_value=1, value=10)
            if st.form_submit_button("Add Link") and a != b:
                st.session_state.links.append({"u": a, "v": b, "w": w})
                st.rerun()

    if st.button("🗑️ Reset Network"):
        st.session_state.nodes = {}
        st.session_state.links = []
        st.rerun()

# ================= BUILD GRAPH =================
if not st.session_state.nodes:
    st.info("Add devices and links from sidebar.")
    st.stop()

G = nx.Graph()
for n, t in st.session_state.nodes.items():
    G.add_node(n, type=t)

for l in st.session_state.links:
    G.add_edge(l["u"], l["v"], weight=l["w"])

# ================= VISUAL =================
st.subheader("🖼️ Network Topology Diagram")
fig, ax = plt.subplots(figsize=(10, 6))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=1500, width=2)
nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "weight"))
st.pyplot(fig)

# ================= SHORTEST PATH =================
st.divider()
st.subheader("🛤️ Shortest Path (Dijkstra)")

src = st.selectbox("Source", list(G.nodes()), key="sp_s")
dst = st.selectbox("Destination", list(G.nodes()), key="sp_d")

ospf_path, ospf_cost = None, None

if st.button("Compute Shortest Path"):
    ospf_path = nx.shortest_path(G, src, dst, weight="weight")
    ospf_cost = nx.shortest_path_length(G, src, dst, weight="weight")
    st.success(" ➔ ".join(ospf_path))
    st.info(f"Total Cost = {ospf_cost}")

# ================= MST =================
mst_cost = None
if nx.is_connected(G):
    mst = nx.minimum_spanning_tree(G, weight="weight")
    mst_cost = sum(mst[u][v]["weight"] for u, v in mst.edges())

# ================= TOPOLOGY IDENTIFICATION =================
st.divider()
st.subheader("🌐 Network Topology Identification")

n = G.number_of_nodes()
e = G.number_of_edges()
degrees = list(dict(G.degree()).values())

topology = "Hybrid Topology"
reason = "Combination of multiple topology characteristics."

if max(degrees) == n - 1 and degrees.count(1) == n - 1:
    topology = "Star Topology"
    reason = "One central node connected to all others."

elif n >= 3 and all(d == 2 for d in degrees):
    topology = "Ring Topology"
    reason = "Each node connected to exactly two neighbors."

elif e == n * (n - 1) // 2:
    topology = "Full Mesh Topology"
    reason = "Every node directly connected to all others."

elif nx.is_tree(G) and degrees.count(1) == 2 and all(d in [1, 2] for d in degrees):
    topology = "Bus Topology"
    reason = "Linear connection with two end devices."

elif nx.is_tree(G):
    topology = "Tree Topology"
    reason = "Hierarchical structure with no cycles."

st.success(f"Detected Topology: **{topology}**")

# ================= FINAL NETWORK IDENTIFIER TABLE =================
st.divider()
st.subheader("📊 Complete Network Identifier & Comparison Table")

final_table = pd.DataFrame([
    {
        "Detected Topology": topology,
        "Topology Reason": reason,
        "OSPF Route": " ➔ ".join(ospf_path) if ospf_path else "Not computed",
        "OSPF Total Cost": ospf_cost if ospf_cost else "N/A",
        "MST Optimized Cost": mst_cost if mst_cost else "N/A",
        "Why This Network Is Best": (
            "Ensures optimal routing via OSPF, minimized infrastructure "
            "cost using MST, and structurally matches detected topology."
        ),
        "Comparison with Other Networks": (
            "Lower cost than Full Mesh, better scalability than Bus, "
            "and more reliable than Ring topology."
        )
    }
])

st.dataframe(final_table, use_container_width=True, hide_index=True)
