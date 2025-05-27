import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
import json
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import requests
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw

# Paths to the similarity matrices
base_path = os.path.dirname(__file__)
matrices = [
    'abilities_sim_matrix.pkl',
    'aggregate_stats_sim_matrix.pkl',
    'basic_stats_sim_matrix.pkl',
    'recommended_items_sim_matrix.pkl',
]
matrices = [os.path.join(base_path, 'model', m) for m in matrices]

# Load matrices
sims = []
for path in matrices:
    with open(path, 'rb') as f:
        sims.append(pickle.load(f))

# Ensure all matrices are numpy arrays and have the same shape
sims = [np.array(s) for s in sims]
# Combine matrices by summing
sim = sum(sim * 0.25 for sim in sims)

# Perform hierarchical clustering
linked = linkage(sim, method='average')
order = leaves_list(linked)

# Reorder the similarity matrix
sim_reordered = sim[order][:, order]

# Plot dendrogram and overlay hero thumbnails as x-axis labels
fig, ax = plt.subplots(figsize=(14, 6))
ddata = dendrogram(linked, labels=None, ax=ax, no_labels=True)
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('Hero')
plt.ylabel('Distance')
plt.tight_layout()

# Get the order of leaves and their x positions
leaf_order = ddata['leaves']

# Get the x positions for each leaf
# Each leaf's x position is the middle of the bottom of the 'U' in icoord
leaf_xs = []
for xs, leaf in zip(ddata['icoord'], ddata['leaves']):
    # The leaf position is always at xs[1] (the second value in icoord for each leaf)
    leaf_xs.append(xs[1])

# Load hero_idx.pkl
with open('api/recommendation_service/model/hero_idx.pkl', 'rb') as f:
    hero_idx = pickle.load(f)  # numpy array, index -> hero_id

# Load heroes.json
with open('api/recommendation_service/heroes.json', 'r', encoding='utf-8') as f:
    heroes = json.load(f)

# Build a mapping from hero_id to image URL
id_to_img = {hero['id']: hero['img'] for hero in heroes}

# Get image URLs for the reordered indices
img_urls = [id_to_img.get(int(hero_idx[i]), None) for i in leaf_order]

# Now overlay images at these positions
for x, url in zip(leaf_xs, img_urls):
    if url:
        try:
            # response = requests.get(url)
            # img = plt.imread(BytesIO(response.content), format='png')
            # imagebox = OffsetImage(img, zoom=0.5)
            # ab = AnnotationBbox(imagebox, (x, 0), frameon=False, box_alignment=(0.5, -0.1))
            # ax.add_artist(ab)

            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            # Make image square
            size = min(img.size)
            img = ImageOps.fit(img, (size, size), centering=(0.5, 0.5))
            # Create circular mask
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            img.putalpha(mask)
            # Convert to numpy array for matplotlib
            img_np = np.array(img)
            imagebox = OffsetImage(img_np, zoom=0.1)  # Adjust zoom as needed
            ab = AnnotationBbox(imagebox, (x, 0), frameon=False, box_alignment=(0.5, -0.2))
            ax.add_artist(ab)
        except Exception as e:
            print(f"Could not load image for hero at position {x}: {e}")

# Optionally, remove x-tick labels
ax.set_xticks([])

# Save the figure first before showing it
plt.savefig(os.path.join(base_path, 'dendrogram.png'), dpi=300, bbox_inches='tight')
plt.show()
plt.close()

print('Clustering and visualization complete. Images saved as dendrogram.png and similarity_heatmap.png.') 