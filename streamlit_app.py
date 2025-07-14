import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import io
import time
import tempfile
import imageio
import plotly.graph_objs as go

st.set_page_config(layout="wide")

# --- Parse CLI File ---
def parse_cli_file(file):
    lines = file.read().decode("utf-8").splitlines()
    toolpath_data = defaultdict(list)
    current_layer = None
    for line in lines:
        if line.startswith("$$LAYER/"):
            current_layer = int(line.strip().split("/")[1])
        elif line.startswith("$$HATCHES") and current_layer is not None:
            parts = line.strip().split(",")[2:]
            coords = list(map(int, parts))
            segment = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
            toolpath_data[current_layer].append(segment)
    return toolpath_data

# --- Heatmap Generator ---
def generate_heatmap(layer_data, grid_size=300, Q=1.0, sigma=0.5):
    points = [(x / 1000, y / 1000) for segment in layer_data for (x, y) in segment]
    if not points:
        return None, None, None
    xs, ys = zip(*points)
    x_min, x_max = min(xs) - 1, max(xs) + 1
    y_min, y_max = min(ys) - 1, max(ys) + 1
    x = np.linspace(x_min, x_max, grid_size)
    y = np.linspace(y_min, y_max, grid_size)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    for x0, y0 in points:
        Z += Q * np.exp(-((X - x0)**2 + (Y - y0)**2) / (2 * sigma**2))
    return X, Y, Z

# --- 2D Heatmap Plotting ---
def plot_layer_with_heat(layer_data, layer_number, return_bytes=False):
    X, Y, Z = generate_heatmap(layer_data)
    fig, ax = plt.subplots(figsize=(8, 6))
    if X is not None:
        ax.contourf(X, Y, Z, levels=50, cmap='hot')
    for segment in layer_data:
        x_vals = [x / 1000 for x, y in segment]
        y_vals = [y / 1000 for x, y in segment]
        ax.plot(x_vals, y_vals, color='cyan', marker='o')
    ax.set_title(f"Layer {layer_number} - Heat Source Overlay")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.axis("equal")
    fig.tight_layout()

    if return_bytes:
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        return buf
    return fig

# --- 3D Plot Using Plotly ---
def plot_3d_toolpath(layer_data, layer_number):
    fig = go.Figure()
    z = layer_number
    for segment in layer_data:
        x = [pt[0]/1000 for pt in segment]
        y = [pt[1]/1000 for pt in segment]
        z_vals = [z] * len(segment)
        fig.add_trace(go.Scatter3d(x=x, y=y, z=z_vals, mode='lines+markers', line=dict(color='blue'), marker=dict(size=3)))
    fig.update_layout(scene=dict(
        xaxis_title="X (mm)", yaxis_title="Y (mm)", zaxis_title="Layer (Z)",
        aspectmode='data'
    ), title=f"3D View - Layer {layer_number}")
    return fig

# --- Streamlit GUI ---
st.title("🧊 Tool Path Visualization with Heat Source Playback")

uploaded_file = st.file_uploader("📁 Upload a .cli file", type=["cli"])
if uploaded_file is not None:
    toolpath_data = parse_cli_file(uploaded_file)
    available_layers = sorted(toolpath_data.keys())

    # Toolpath stats
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Toolpath Stats")
        st.write(f"**Total Layers:** {len(available_layers)}")
        total_segments = sum(len(v) for v in toolpath_data.values())
        total_points = sum(len(s) for v in toolpath_data.values() for s in v)
        st.write(f"**Total Segments:** {total_segments}")
        st.write(f"**Total Points:** {total_points}")

    with col2:
        layer_number = st.selectbox("🧱 Select Layer to Visualize", available_layers)
        layer_data = toolpath_data[layer_number]
        total_layer_points = sum(len(s) for s in layer_data)

        autoplay = st.checkbox("▶️ Autoplay animation")
        speed = st.slider("⏱️ Speed (frames/sec)", 1, 30, 5)
        frame = 1

        # Playback
        if autoplay:
            play_area = st.empty()
            for i in range(1, total_layer_points + 1):
                frame = i
                limited_data = []
                point_count = 0
                for segment in layer_data:
                    seg = []
                    for pt in segment:
                        if point_count < frame:
                            seg.append(pt)
                            point_count += 1
                        else:
                            break
                    if seg:
                        limited_data.append(seg)
                    if point_count >= frame:
                        break
                fig = plot_layer_with_heat(limited_data, layer_number)
                play_area.pyplot(fig)
                time.sleep(1 / speed)
        else:
            frame = st.slider("🎞️ Manual Playback Frame", 1, total_layer_points, 1, step=1)

            limited_data = []
            point_count = 0
            for segment in layer_data:
                seg = []
                for pt in segment:
                    if point_count < frame:
                        seg.append(pt)
                        point_count += 1
                    else:
                        break
                if seg:
                    limited_data.append(seg)
                if point_count >= frame:
                    break
            fig = plot_layer_with_heat(limited_data, layer_number)
            st.pyplot(fig)

    # Export heatmap PNG
    buf = plot_layer_with_heat(layer_data, layer_number, return_bytes=True)
    st.download_button("💾 Download Full Heatmap as PNG", data=buf, file_name=f"layer_{layer_number}.png", mime="image/png")

    # Compare two layers
    with st.expander("🆚 Compare Two Layers Side-by-Side"):
        col_a, col_b = st.columns(2)
        with col_a:
            layer_a = st.selectbox("Layer A", available_layers, index=0, key="layer_a")
        with col_b:
            layer_b = st.selectbox("Layer B", available_layers, index=1, key="layer_b")

        if st.button("Show Comparison"):
            fig1 = plot_layer_with_heat(toolpath_data[layer_a], layer_a)
            fig2 = plot_layer_with_heat(toolpath_data[layer_b], layer_b)
            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(fig1)
            with col2:
                st.pyplot(fig2)

    # Export GIF animation
    with st.expander("🎬 Export Animated Heatmap as GIF"):
        if st.button("Generate & Download GIF"):
            frames = []
            with st.spinner("Generating frames..."):
                for i in range(1, total_layer_points + 1):
                    frame_data = []
                    count = 0
                    for seg in layer_data:
                        temp_seg = []
                        for pt in seg:
                            if count < i:
                                temp_seg.append(pt)
                                count += 1
                            else:
                                break
                        if temp_seg:
                            frame_data.append(temp_seg)
                        if count >= i:
                            break
                    fig = plot_layer_with_heat(frame_data, layer_number)
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png")
                    buf.seek(0)
                    image = imageio.v2.imread(buf)
                    frames.append(image)

            tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".gif")
            imageio.mimsave(tmpfile.name, frames, fps=speed)
            with open(tmpfile.name, "rb") as f:
                st.download_button("📥 Download Animation GIF", f, file_name=f"layer_{layer_number}_playback.gif", mime="image/gif")

    # 3D Viewer
    st.markdown("### 🧊 3D Tool Path Viewer")
    st.plotly_chart(plot_3d_toolpath(layer_data, layer_number), use_container_width=True)
