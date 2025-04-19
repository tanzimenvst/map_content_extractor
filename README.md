# 🗺️ Map Content Extractor

This repository provides a Python based tool to extract only the **core map content** from large cartographic raster images (e.g., GeoTIFFs), eliminating surrounding non-essential elements such as legends, scale bars, titles, and decorative margins.
This is particularly useful for scanned maps, atlases, or historical datasets where the actual map area needs to be isolated for further GIS analysis.

---

## 📸 What It Does — Visual Overview

<p align="center">
  <img src="assets/Demo.jpg" alt="Demo"/>
</p>


---

## 📂 Input Image Criteria

- The tool works on **single-band colormap raster images**.
- Assumes that **a uniform color (e.g., white or nodata)** surrounds the main map content.
- Image should have **consistent color padding** around the map for accurate detection.

---

## ⚙️ Features

🎯 Detects specific colored regions (e.g., white/nodata) using pixel value analysis  
🗺️ Automatically identifies and retains the largest valid map area  
🧼 Applies geometric operations:
  - `Erase` 
  - `Buffer`  
  - `Shape simplification` 
✂️ Clips the raster using the extracted polygon  
🎨 Re-applies the original colormap to the final output

---

## 🧰 Dependencies

Make sure you have the following installed:

- [ArcPy (requires ArcGIS Pro)](https://pro.arcgis.com/en/pro-app/arcpy/get-started/what-is-arcpy-.htm)
- [Rasterio](https://rasterio.readthedocs.io/)  
- [GeoPandas](https://geopandas.org/)  
- [Fiona](https://fiona.readthedocs.io/)  
- [Shapely](https://shapely.readthedocs.io/)

Install Python packages (except ArcPy, which comes with ArcGIS Pro) via:

```bash
conda install -c conda-forge rasterio geopandas fiona shapely
```

---

## 🚀 Usage

Update the following paths in the script before running:

```python
input_image = r"path\to\your\map_image.tif"
output_path = r"path\to\output\folder"
```

Then run the script in your Python environment (ArcGIS Pro recommended):

```bash
python extract_map_content.py
```

---

## 📦 Output

- `*_clipped.tif` – Cropped GeoTIFF with only core map content
- `/temp/` – Folder with intermediate shapefiles used for processing, can be deleted after completed.

---

## 📝 Notes

- Works best with high-resolution, clearly bordered raster maps.
- Assumes a rectangular boundary around the map with detectable border color (like white).
- The buffer distance and simplification parameters can be adjusted as needed.
