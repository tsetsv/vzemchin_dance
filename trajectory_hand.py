import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# -----------------------------
# BVH Joint классын тодорхойлолт
# -----------------------------
class Joint:
    def __init__(self, name, offset, channels, parent=None):
        self.name = name
        self.offset = np.array(offset, dtype=float)
        self.channels = channels
        self.parent = parent
        self.children = []
        if parent:
            parent.children.append(self)

# -----------------------------
# BVH файл унших функц
# -----------------------------
def read_bvh(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    joints = []
    stack = []
    motion_index = 0

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("ROOT") or line.startswith("JOINT"):
            name = line.split()[1]
            i += 1  # '{'
            i += 1
            offset = list(map(float, lines[i].split()[1:]))
            i += 1
            channels = []
            if "CHANNELS" in lines[i]:
                channels = lines[i].split()[2:]
                i += 1
            parent = stack[-1] if stack else None
            joint = Joint(name, offset, channels, parent)
            joints.append(joint)
            stack.append(joint)
        elif line.startswith("End Site"):
            i += 1  # '{'
            i += 1  # OFFSET
            i += 1  # '}'
        elif line == "}":
            if stack:
                stack.pop()
            i += 1
        elif line.startswith("MOTION"):
            motion_index = i + 1
            break
        else:
            i += 1

    # --- Motion хэсгийг унших ---
    frame_time_line = lines[motion_index + 1]
    frame_time = float(frame_time_line.split(":")[1].strip())
    motion_data = np.array(
        [list(map(float, line.strip().split())) for line in lines[motion_index + 2:] if line.strip()]
    )

    return joints, motion_data, frame_time

# -----------------------------
# Бугуйн траектори тооцох функц
# -----------------------------
def get_joint_trajectory(joints, motion_data, joint_name):
    joint_names = [j.name for j in joints]
    if joint_name not in joint_names:
        raise ValueError(f"Joint '{joint_name}' not found! Available joints: {joint_names}")

    # BVH файлын ROOT нь эхний 3 байрлал + 3 эргэлтийн channel-тэй байдаг
    root_pos = motion_data[:, :3]
    return root_pos

# -----------------------------
# Гол код (Main)
# -----------------------------
if __name__ == "__main__":
    bvh_path = "DATA/vnuman_1c3.bvh"   # <-- Өөрийн BVH файлын замыг энд бичээрэй
    joints, motion_data, frame_time = read_bvh(bvh_path)

    # --- Гарны бугуйн нэрийг BVH файлд тааруулах ---
    LeftHand = "LeftHandThumb1"    # Зарим BVH-д "LeftWrist" эсвэл "LeftHandEnd" гэж байж болно
    RightHand = "RightHandThumb1"  # Түүнчлэн "RightWrist", "RightHandEnd" гэх мэт байж болно

    # --- Бугуйн траектори авах ---
    left_traj = get_joint_trajectory(joints, motion_data, LeftHand)
    right_traj = get_joint_trajectory(joints, motion_data, RightHand)

    # -----------------------------
    # 3D Траектори дүрслэл
    # -----------------------------
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Зүүн гар — улаан
    ax.plot(left_traj[:, 0], left_traj[:, 2], left_traj[:, 1],
            color='red', label='Left Hand Trajectory', linewidth=2)

    # Баруун гар — цэнхэр
    ax.plot(right_traj[:, 0], right_traj[:, 2], right_traj[:, 1],
            color='blue', label='Right Hand Trajectory', linewidth=2)

    # Хязгаар ба харагдац
    ax.set_xlim([-100, 100])
    ax.set_ylim([-100, 100])
    ax.set_zlim([0, 200])
    ax.view_init(elev=10, azim=90)

    ax.set_title("3D Wrist Trajectories from BVH", fontsize=13)
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Z Axis")
    ax.set_zlabel("Y Axis")
    ax.legend()
    plt.tight_layout()
    plt.show()
