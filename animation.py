import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- 1. TRC файл унших ---
def load_trc(file_path):
    df = pd.read_csv(file_path, sep='\t', skiprows=6)
    data = df.to_numpy()
    data = np.nan_to_num(data)
    total_cols = data.shape[1] - (data.shape[1] % 3)
    data = data[:, :total_cols]
    frames = data.reshape((data.shape[0], total_cols//3, 3))
    return frames

frames = load_trc("shot1_004.trc")
num_frames, num_points, _ = frames.shape

# --- 2. XY проекц ---
def project_xy(frame):
    return frame[:, [0, 1]]

# --- 3. Animation бэлтгэх ---
fig, ax = plt.subplots(figsize=(8,8))
ax.set_facecolor('black')
ax.set_xlim(-500, 500)
ax.set_ylim(-500, 500)
ax.set_aspect('equal')
ax.axis('off')

# --- 4. Update function ---
def update(frame_idx):
    ax.clear()
    ax.set_facecolor('black')
    ax.axis('off')
    ax.set_xlim(-500, 500)
    ax.set_ylim(-500, 500)
    ax.set_aspect('equal')
    
    frame = frames[frame_idx]
    proj = project_xy(frame)
    
    # Random цэг нэмэх
    extra_points = proj + np.random.normal(0, 5, proj.shape)
    combined = np.vstack([proj, extra_points])
    
    # Том цэг, цагаан өнгө
    ax.scatter(combined[:,0], combined[:,1], s=1, color='black', alpha=1)

# --- 5. Animation тоглуулах ---
anim = FuncAnimation(fig, update, frames=num_frames, interval=33)
plt.show()
