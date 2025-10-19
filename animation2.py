from bvh import Bvh
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math

# --- 1. BVH файл унших ---
with open("shot1_004_Skeleton_002.bvh") as f:
    mocap = Bvh(f.read())

frames_data = np.array(mocap.frames, dtype=float)
num_frames = frames_data.shape[0]

# --- 2. Joint hierarchy, channels ---
joints = mocap.get_joints_names()
joint_channels_idx = {}
idx = 0
for j in joints:
    channels = mocap.joint_channels(j)
    joint_channels_idx[j] = list(range(idx, idx + len(channels)))
    idx += len(channels)

# parent dictionary, ROOT-г None
joint_parents = {}

def build_parents(node, parent=None):
    # End Site эсэхийг шалгах
    try:
        name = node.name  # ROOT, JOINT-д ажиллана
    except IndexError:
        # End Site-д нэр өгөх
        name = "EndSite_" + (parent if parent else "ROOT")
    joint_parents[name] = parent

    # JOINT-г traverse хийх
    for child in node.filter('JOINT'):
        build_parents(child, name)
    
    # End Site-г traverse хийх
    for child in node.filter('End'):
        build_parents(child, name)

# ROOT node-оос эхлэх
build_parents(mocap.root)


# --- 3. Helper: rotation matrix ---
def rot_matrix_xyz(rx, ry, rz):
    # Degrees to radians
    rx, ry, rz = np.deg2rad([rx, ry, rz])
    Rx = np.array([[1,0,0],
                   [0,np.cos(rx), -np.sin(rx)],
                   [0,np.sin(rx), np.cos(rx)]])
    Ry = np.array([[np.cos(ry),0,np.sin(ry)],
                   [0,1,0],
                   [-np.sin(ry),0,np.cos(ry)]])
    Rz = np.array([[np.cos(rz), -np.sin(rz),0],
                   [np.sin(rz), np.cos(rz),0],
                   [0,0,1]])
    return Rz @ Ry @ Rx

# --- 4. Global joint positions ---
def get_global_positions(frame_idx):
    positions = {}
    def traverse(node, parent_pos=np.zeros(3), parent_rot=np.eye(3)):
        name = node.name
        channels = mocap.joint_channels(name)
        indices = joint_channels_idx[name]
        pos = np.array([0,0,0])
        rot = np.eye(3)

        if 'Xposition' in channels:
            xi = indices[channels.index('Xposition')]
            yi = indices[channels.index('Yposition')]
            zi = indices[channels.index('Zposition')]
            pos = np.array([frames_data[frame_idx, xi],
                            frames_data[frame_idx, yi],
                            frames_data[frame_idx, zi]])
        # Rotation
        rot_idx = []
        for c in ['Xrotation','Yrotation','Zrotation']:
            if c in channels:
                rot_idx.append(indices[channels.index(c)])
            else:
                rot_idx.append(None)
        rx = frames_data[frame_idx, rot_idx[0]] if rot_idx[0] is not None else 0
        ry = frames_data[frame_idx, rot_idx[1]] if rot_idx[1] is not None else 0
        rz = frames_data[frame_idx, rot_idx[2]] if rot_idx[2] is not None else 0
        rot = rot_matrix_xyz(rx, ry, rz)

        # End Site offset
        offset = np.array(node['OFFSET'], dtype=float)
        global_pos = parent_pos + parent_rot @ (pos + offset)
        positions[name] = global_pos

        # Traverse children
        for child in node.filter('JOINT'):
            traverse(child, global_pos, parent_rot @ rot)
        for child in node.filter('End'):
            offset_end = np.array(child['OFFSET'], dtype=float)
            positions[child.name] = global_pos + parent_rot @ rot @ offset_end

    traverse(mocap.root)
    return positions

# --- 5. Matplotlib animation ---
fig, ax = plt.subplots(figsize=(8,12))
ax.set_facecolor('white')  # цагаан дэвсгэр
ax.set_xlim(-100, 100)
ax.set_ylim(0, 250)  # урдаас харах (Y=height)
ax.set_aspect('equal')
ax.axis('off')

frame_step = 10  # frame-г алгасаж хурдан
lines = []

# Connect joints: skeletal structure
connections = []
def build_connections(node):
    for child in node.filter('JOINT'):
        connections.append((node.name, child.name))
        build_connections(child)
    for child in node.filter('End'):
        connections.append((node.name, child.name))
build_connections(mocap.root)

def update(frame_idx):
    ax.clear()
    ax.set_facecolor('white')
    ax.set_xlim(-100, 100)
    ax.set_ylim(0, 250)
    ax.set_aspect('equal')
    ax.axis('off')

    positions = get_global_positions(frame_idx)
    xs, ys = [], []
    for p in positions.values():
        xs.append(p[0])
        ys.append(p[1])
    ax.scatter(xs, ys, s=20, color='black')

    # Draw bones
    for c in connections:
        p1 = positions[c[0]]
        p2 = positions[c[1]]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='black', linewidth=2)

anim = FuncAnimation(fig, update, frames=range(0, num_frames, frame_step), interval=33)
plt.show()
