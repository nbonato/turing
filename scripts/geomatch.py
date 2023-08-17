import json
from shapely.geometry import shape, GeometryCollection, Point
with open('geodata/updated_map.json', 'r') as f:
    js = json.load(f)

coords = [(0, 0), (1, 1)]

