import os
import arcpy
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
import fiona
import matplotlib.pyplot as plt
from shapely.geometry import box, shape, mapping, Polygon, JOIN_STYLE


# USER INPUTS
input_image = r"D:\Work\My Work\map_content_extractor\San_Francisco\San Francisco SEC.tif"
output_path = r"D:\Work\My Work\map_content_extractor\Output"



# Creating temp folder
temp = f"{output_path}\\temp"
if not os.path.exists(temp):
    os.makedirs(temp)


# Extracting extent and white pixels
extent_shp = f"{temp}\\extent.shp"
white_pixels_shp = f"{temp}\\white_pixels.shp"

with rasterio.open(input_image) as src:
    transform = src.transform
    bounds = src.bounds
    crs = src.crs.to_dict()
    data = src.read(1)

    # Step 1: Creating extent polygon
    extent_geom = box(bounds.left, bounds.bottom, bounds.right, bounds.top)

    with fiona.open(
        extent_shp, 'w',
        driver='ESRI Shapefile',
        crs=crs,
        schema={'geometry': 'Polygon', 'properties': {}}
    ) as dst:
        dst.write({'geometry': mapping(extent_geom), 'properties': {}})

    # Step 2: Identifying white pixels
    white_mask = (data == 0)

    shapes_gen = shapes(
        white_mask.astype(np.uint8),
        mask=white_mask,
        transform=transform
    )

    with fiona.open(
        white_pixels_shp, 'w',
        driver='ESRI Shapefile',
        crs=crs,
        schema={'geometry': 'Polygon', 'properties': {}}
    ) as dst:
        for geom, val in shapes_gen:
            dst.write({'geometry': geom, 'properties': {}})


# Extracting largest feature of white pixels shp
white_largest = f"{temp}\\white_largest.shp"
gdf = gpd.read_file(white_pixels_shp)

# Reprojecting if CRS is geographic (for accurate area calculation)
if gdf.crs.is_geographic:
    gdf = gdf.to_crs(epsg=3857)

# Calculating area and find index of the largest polygon
gdf['area'] = gdf.geometry.area
largest_index = gdf['area'].idxmax()

# Keepping only the largest polygon
largest_gdf = gdf.loc[[largest_index]].drop(columns='area')

# Saving it to a new shapefile
largest_gdf.to_file(white_largest)


# Erasing from extent
output_erased = f"{temp}\\erased_output.shp"
arcpy.analysis.Erase(extent_shp, white_largest, output_erased)


# Exploding Multipart to Singlepart
exploded_output = f"{temp}\\exploded_output.shp"
arcpy.management.MultipartToSinglepart(output_erased, exploded_output)


# Extracting largest feature
exploded_largest = f"{temp}\\exploded_largest.shp"
gdf = gpd.read_file(exploded_output)

# Reprojecting if CRS is geographic (for accurate area calculation)
if gdf.crs.is_geographic:
    gdf = gdf.to_crs(epsg=3857)

# Calculating area and find index of the largest polygon
gdf['area'] = gdf.geometry.area
largest_index = gdf['area'].idxmax()

# Keepping only the largest polygon
largest_gdf = gdf.loc[[largest_index]].drop(columns='area')

# Saving it to a new shapefile
largest_gdf.to_file(exploded_largest)


# Converting polygon To Line
white_line_shp = f"{temp}\\white_line.shp"
arcpy.management.PolygonToLine(exploded_largest, white_line_shp, "FALSE")


# Simplifying Line
white_line_simplify = f"{temp}\\white_line_simplify.shp"
arcpy.cartography.SimplifyLine(white_line_shp, white_line_simplify, "POINT_REMOVE", "100 Meters", "RESOLVE_ERRORS", "NO_KEEP", "CHECK", None)


# Buffering with 5000 units
buffer = f"{temp}\\buffer.shp"
arcpy.analysis.PairwiseBuffer(white_line_simplify, buffer, "5000 Meters", "NONE", None, "PLANAR", "0 Meters")


# Converting Polygon To Line
buffer_line_shp = f"{temp}\\buffer_line_shp.shp"
arcpy.management.PolygonToLine(buffer, buffer_line_shp, "FALSE")


# Converting line to polygon
buffer_polygon = f"{temp}\\buffer_polygon.shp"
arcpy.management.FeatureToPolygon(buffer_line_shp, buffer_polygon, None, "ATTRIBUTES", None)


# Extracting largest feature
largest_buffer_polygon = f"{temp}\\largest_buffer_polygon.shp"
gdf = gpd.read_file(buffer_polygon)

# Reprojecting if CRS is geographic (for accurate area calculation)
if gdf.crs.is_geographic:
    gdf = gdf.to_crs(epsg=3857)

# Calculating area and find index of the largest polygon
gdf['area'] = gdf.geometry.area
largest_index = gdf['area'].idxmax()

# Keepping only the largest polygon
largest_gdf = gdf.loc[[largest_index]].drop(columns='area')

# Saving it to a new shapefile
largest_gdf.to_file(largest_buffer_polygon)


# Getting cell size
desc = arcpy.Describe(input_image)
cell_width = desc.meanCellWidth
cell_height = desc.meanCellHeight

# Calculate decimal part
if cell_width == cell_height:
    cell_size = int(cell_width)
else:
    avg = (cell_width + cell_height) / 2
    cell_size = int(avg)


# Buffering with flat end type
final_buffer = f"{temp}\\final_buffer.shp"

# Load your polygon shapefile
gdf = gpd.read_file(largest_buffer_polygon)

# Create outside buffer with flat/square corners (join_style=2 = mitre)
gdf_buffered = gdf.copy()
gdf_buffered["geometry"] = gdf.geometry.buffer(5000-cell_size, join_style=2)

# Save to new shapefile
gdf_buffered.to_file(final_buffer)


# Extracting output image
filename, extension = os.path.basename(input_image).split('.')
output_raster = f"{output_path}\\{filename}_clipped.{extension}"

masked = arcpy.sa.ExtractByMask(input_image, final_buffer)
masked.save(output_raster)


# Applying the colormap from source
arcpy.management.AddColormap(output_raster, input_image, None)

print("Map content extracted successfully.")