3D Tool Path Visualizer with Heat Source Overlay 

A Streamlit-based tool to visualize 3D printing toolpaths (from `.cli` files) with thermal overlays simulating Gaussian heat source behavior.

---

Features

-upload cli file
- CLI file parsing and 2D/3D visualization
- Gaussian-based heat map overlay
- Layer selection and animation
- Export images and GIFs
- Toolpath statistics and 3D view
- Multiple layer comparison
- Autplay at selected speed

---

Sample CLI File Format

```cli
$$LAYER/0.2
10.0 10.0
15.0 15.0
$$LAYER/0.4
12.0 12.0
16.0 18.0

---

.cli file parasing logic

---
-Line by line wil be read by the parser
- A new layer denotes by $$LAYER/x.x
-Each line after it is a coordinate pair (x,y)
-Also it combined with thhe Z-value to form (X,Y,Z) points

---

Heat Source Modeling

---

-Gaussian heat model was used
exp(-((x - cx)^2 + (y - cy)^2) / (2 * sigma^2))
-Centered at each toolpath point.
-Visualized as a heatmap overlay.
-Sigma controls the spread of heat.

---

GUI Structure

---

-Built with Streamlit
-Upload .cli file → choose layer → view path and heat
-Autoplay at different speeds
-Optional 3D viewer (Plotly)
-Export tools (Image / Animated GIF)
-Statistics (layer count, point count)

---

How to run

---

-Clone the repo
git clone https://github.com/YOUR_USERNAME/3DToolpath-Visualizer.git
cd 3DToolpath-Visualizer

-Install dependancies
pip install -r requirements.txt

-Run the app
streamlit run streamlit_app.py

---

Dependencies

streamlit
numpy
matplotlib
imageio
plotly


