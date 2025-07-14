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
