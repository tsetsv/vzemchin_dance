import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

class BVHParser:
    def __init__(self, filename):
        self.filename = filename
        self.joints = {}
        self.joint_names = []
        self.hierarchy = []
        self.frames = []
        self.frame_time = 0
        self.root = None
        
    def parse(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('ROOT'):
                self.root, i = self._parse_joint(lines, i, None)
            elif line.startswith('MOTION'):
                i = self._parse_motion(lines, i)
            else:
                i += 1
        
        return self
    
    def _parse_joint(self, lines, idx, parent):
        line = lines[idx].strip()
        parts = line.split()
        joint_type = parts[0]
        joint_name = parts[1]
        
        joint = {
            'name': joint_name,
            'parent': parent,
            'offset': [0, 0, 0],
            'channels': [],
            'children': []
        }
        
        self.joint_names.append(joint_name)
        self.joints[joint_name] = joint
        
        idx += 1
        while idx < len(lines):
            line = lines[idx].strip()
            
            if line.startswith('OFFSET'):
                parts = line.split()
                joint['offset'] = [float(parts[1]), float(parts[2]), float(parts[3])]
                idx += 1
                
            elif line.startswith('CHANNELS'):
                parts = line.split()
                num_channels = int(parts[1])
                joint['channels'] = parts[2:2+num_channels]
                idx += 1
                
            elif line.startswith('JOINT'):
                child, idx = self._parse_joint(lines, idx, joint_name)
                joint['children'].append(child)
                
            elif line.startswith('End Site'):
                idx += 1
                while idx < len(lines):
                    line = lines[idx].strip()
                    if line.startswith('OFFSET'):
                        parts = line.split()
                        end_site = {
                            'name': joint_name + '_end',
                            'parent': joint_name,
                            'offset': [float(parts[1]), float(parts[2]), float(parts[3])],
                            'channels': [],
                            'children': [],
                            'is_end': True
                        }
                        joint['children'].append(end_site)
                        idx += 1
                    elif line == '}':
                        idx += 1
                        break
                    else:
                        idx += 1
                        
            elif line == '}':
                idx += 1
                break
            else:
                idx += 1
                
        return joint, idx
    
    def _parse_motion(self, lines, idx):
        idx += 1
        while idx < len(lines):
            line = lines[idx].strip()
            if line.startswith('Frames:'):
                num_frames = int(line.split(':')[1].strip())
                idx += 1
            elif line.startswith('Frame Time:'):
                self.frame_time = float(line.split(':')[1].strip())
                idx += 1
                break
            else:
                idx += 1
        
        # Parse frame data
        while idx < len(lines):
            line = lines[idx].strip()
            if line:
                values = [float(x) for x in line.split()]
                self.frames.append(values)
            idx += 1
            
        return idx
    
    def get_skeleton_data(self, frame_idx):
        """Returns points and connections for the skeleton"""
        if frame_idx >= len(self.frames):
            frame_idx = len(self.frames) - 1
            
        frame_data = self.frames[frame_idx]
        points = []
        connections = []
        joint_positions = {}
        
        channel_idx = 0
        
        def process_joint(joint, parent_transform, parent_idx):
            nonlocal channel_idx
            
            # Create local transform with offset
            offset = np.array(joint['offset'])
            local_transform = np.eye(4)
            
            # Apply rotations first, then translation
            rotation_matrix = np.eye(4)
            
            if joint['channels']:
                # Collect rotation values
                rotations = {}
                for channel in joint['channels']:
                    if channel_idx < len(frame_data):
                        value = frame_data[channel_idx]
                        channel_idx += 1
                        
                        if 'position' in channel:
                            axis = channel[0].lower()
                            if axis == 'x':
                                offset[0] = value
                            elif axis == 'y':
                                offset[1] = value
                            elif axis == 'z':
                                offset[2] = value
                        elif 'rotation' in channel:
                            rotations[channel[0].lower()] = np.radians(value)
                
                # Apply rotations in the order specified in channels
                for channel in joint['channels']:
                    if 'rotation' in channel:
                        axis = channel[0].lower()
                        if axis in rotations:
                            angle = rotations[axis]
                            
                            if axis == 'x':
                                rot = np.array([[1, 0, 0],
                                              [0, np.cos(angle), -np.sin(angle)],
                                              [0, np.sin(angle), np.cos(angle)]])
                            elif axis == 'y':
                                rot = np.array([[np.cos(angle), 0, np.sin(angle)],
                                              [0, 1, 0],
                                              [-np.sin(angle), 0, np.cos(angle)]])
                            elif axis == 'z':
                                rot = np.array([[np.cos(angle), -np.sin(angle), 0],
                                              [np.sin(angle), np.cos(angle), 0],
                                              [0, 0, 1]])
                            
                            rot4 = np.eye(4)
                            rot4[:3, :3] = rot
                            rotation_matrix = rotation_matrix @ rot4
            
            # Apply rotation then translation
            local_transform = rotation_matrix
            local_transform[:3, 3] = offset
            
            # Calculate world transform
            world_transform = parent_transform @ local_transform
            
            # Get world position
            world_pos = world_transform[:3, 3]
            current_idx = len(points)
            points.append(world_pos)
            joint_positions[joint['name']] = current_idx
            
            # Add connection to parent
            if parent_idx is not None:
                connections.append((parent_idx, current_idx))
            
            # Process children
            for child in joint['children']:
                process_joint(child, world_transform, current_idx)
        
        process_joint(self.root, np.eye(4), None)
        
        return np.array(points), connections

def create_pointcloud_video(bvh_file, output_file='skeleton_animation.mp4', fps=30):
    try:
        import imageio
        use_imageio = True
        print("imageio ашиглан video үүсгэнэ...")
    except ImportError:
        use_imageio = False
        print("imageio олдсонгүй. Зургуудыг frames/ хавтасанд хадгална...")
    
    # Parse BVH
    print("BVH файл уншиж байна...")
    parser = BVHParser(bvh_file)
    parser.parse()
    
    print(f"Frames: {len(parser.frames)}")
    print(f"Frame time: {parser.frame_time}")
    
    # Calculate frame skip
    frame_skip = max(1, int((1.0 / parser.frame_time) / fps))
    frames_to_render = range(0, len(parser.frames), frame_skip)
    
    print(f"Нийт render хийх frames: {len(frames_to_render)}")
    
    # Get all points to calculate limits
    print("Харьцаа тооцоолж байна...")
    all_points = []
    step = max(1, len(parser.frames) // 100)
    for i in range(0, len(parser.frames), step):
        pts, _ = parser.get_skeleton_data(i)
        all_points.extend(pts)
    
    all_points = np.array(all_points)
    margin = 20
    xlim = [all_points[:, 0].min() - margin, all_points[:, 0].max() + margin]
    ylim = [all_points[:, 1].min() - margin, all_points[:, 1].max() + margin]
    zlim = [all_points[:, 2].min() - margin, all_points[:, 2].max() + margin]
    
    if use_imageio:
        # Create video using imageio
        images = []
        
        for idx, frame in enumerate(frames_to_render):
            if idx % 50 == 0:
                print(f"Progress: {idx}/{len(frames_to_render)}")
            
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            points, connections = parser.get_skeleton_data(frame)
            
            # Draw connections (bones)
            for conn in connections:
                p1, p2 = points[conn[0]], points[conn[1]]
                ax.plot([p1[0], p2[0]], [p1[2], p2[2]], [p1[1], p2[1]], 
                       'b-', linewidth=2, alpha=0.7)
            
            # Draw joints
            ax.scatter(points[:, 0], points[:, 2], points[:, 1], 
                      c='red', marker='o', s=5, alpha=0.8)
            
            ax.set_xlim(xlim)
            ax.set_ylim(zlim)
            ax.set_zlim(ylim)
            ax.view_init(elev=10, azim=90)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Z')
            ax.set_zlabel('Y')
            ax.set_title(f'Frame {frame}/{len(parser.frames)}')
            
            # Convert to image
            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.buffer_rgba(), dtype='uint8')
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (4,))
            image = image[:, :, :3]  # Remove alpha channel
            images.append(image)
            
            plt.close(fig)
        
        print(f"Video хадгалж байна: {output_file}")
        try:
            imageio.mimsave(output_file, images, fps=fps)
            print(f"Амжилттай! Video хадгалагдлаа: {output_file}")
        except ValueError as e:
            # Fallback to GIF if MP4 not supported
            gif_file = output_file.replace('.mp4', '.gif')
            print(f"MP4 дэмжигдэхгүй байна. GIF үүсгэж байна: {gif_file}")
            imageio.mimsave(gif_file, images, fps=fps, loop=0)
            print(f"Амжилттай! GIF хадгалагдлаа: {gif_file}")
        
    else:
        # Save individual frames
        output_dir = "frames"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Зургуудыг {output_dir}/ хавтасанд хадгалж байна...")
        
        for idx, frame in enumerate(frames_to_render):
            if idx % 50 == 0:
                print(f"Progress: {idx}/{len(frames_to_render)}")
            
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            points, connections = parser.get_skeleton_data(frame)
            
            # Draw connections (bones)
            for conn in connections:
                p1, p2 = points[conn[0]], points[conn[1]]
                ax.plot([p1[0], p2[0]], [p1[2], p2[2]], [p1[1], p2[1]], 
                       'b-', linewidth=2, alpha=0.7)
            
            # Draw joints
            ax.scatter(points[:, 0], points[:, 2], points[:, 1], 
                      c='red', marker='o', s=5, alpha=0.8)
            
            ax.set_xlim(xlim)
            ax.set_ylim(zlim)
            ax.set_zlim(ylim)
            ax.view_init(elev=10, azim=90)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Z')
            ax.set_zlabel('Y')
            ax.set_title(f'Frame {frame}/{len(parser.frames)}')
            
            plt.savefig(f"{output_dir}/frame_{idx:05d}.png", dpi=100)
            plt.close(fig)
        
        print(f"Амжилттай! {len(frames_to_render)} зураг хадгалагдлаа.")
        print(f"Video үүсгэхийн тулд FFmpeg суулгана уу:")
        print(f"  ffmpeg -framerate {fps} -i {output_dir}/frame_%05d.png -c:v libx264 -pix_fmt yuv420p {output_file}")

# Usage
if __name__ == "__main__":
    import sys
    bvh_file = "tasalsan60.bvh"
    output_file = "skeleton_pointcloud5.mp4"
    
    if not os.path.exists(bvh_file):
        print(f"Алдаа: {bvh_file} файл олдсонгүй!")
        sys.exit(1)
    
    create_pointcloud_video(bvh_file, output_file, fps=30)