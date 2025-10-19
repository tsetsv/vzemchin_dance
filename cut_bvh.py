import os
import sys

def cut_bvh_file(input_file, output_file, duration_seconds=180):
    """
    BVH файлыг тодорхой хугацаагаар таслах
    
    Args:
        input_file: Оролтын BVH файл
        output_file: Гаралтын BVH файл
        duration_seconds: Таслах хугацаа (секундээр)
    """
    print(f"BVH файл уншиж байна: {input_file}")
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Find MOTION section
    motion_line_idx = None
    frames_line_idx = None
    frame_time_line_idx = None
    data_start_idx = None
    
    for i, line in enumerate(lines):
        if line.strip() == 'MOTION':
            motion_line_idx = i
        elif line.strip().startswith('Frames:'):
            frames_line_idx = i
            total_frames = int(line.split(':')[1].strip())
        elif line.strip().startswith('Frame Time:'):
            frame_time_line_idx = i
            frame_time = float(line.split(':')[1].strip())
            data_start_idx = i + 1
            break
    
    if motion_line_idx is None or frames_line_idx is None:
        print("Алдаа: BVH форматыг уншиж чадсангүй!")
        return
    
    # Calculate number of frames to keep
    frames_to_keep = int(duration_seconds / frame_time)
    frames_to_keep = min(frames_to_keep, total_frames)
    
    print(f"Нийт frames: {total_frames}")
    print(f"Frame time: {frame_time} сек")
    print(f"Нийт хугацаа: {total_frames * frame_time:.2f} сек")
    print(f"Таслах хугацаа: {duration_seconds} сек")
    print(f"Хадгалах frames: {frames_to_keep}")
    print(f"Шинэ хугацаа: {frames_to_keep * frame_time:.2f} сек")
    
    # Create output content
    output_lines = []
    
    # Copy hierarchy section
    for i in range(motion_line_idx + 1):
        output_lines.append(lines[i])
    
    # Add motion header
    output_lines.append(f"Frames:    {frames_to_keep}\n")
    output_lines.append(f"Frame Time:    {frame_time}\n")
    
    # Add motion data (only first N frames)
    for i in range(data_start_idx, data_start_idx + frames_to_keep):
        if i < len(lines):
            output_lines.append(lines[i])
    
    # Write output file
    print(f"Шинэ файл үүсгэж байна: {output_file}")
    with open(output_file, 'w') as f:
        f.writelines(output_lines)
    
    print(f"Амжилттай! {output_file} файл үүсгэгдлээ.")

# Usage
if __name__ == "__main__":
    # Find .bvh file in current directory
    bvh_files = [f for f in os.listdir('.') if f.endswith('.bvh')]
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    elif bvh_files:
        input_file = bvh_files[0]
        print(f"Файл ашиглаж байна: {input_file}")
    else:
        print("Алдаа: .bvh файл олдсонгүй!")
        print("Хэрэглэх арга:")
        print("  python cut_bvh.py input.bvh")
        print("  python cut_bvh.py input.bvh output.bvh 15")
        sys.exit(1)
    
    # Output file name
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = "tasalsan180.bvh"
    
    # Duration in seconds
    if len(sys.argv) > 3:
        duration = float(sys.argv[3])
    else:
        duration = 180
    
    if not os.path.exists(input_file):
        print(f"Алдаа: {input_file} файл олдсонгүй!")
        sys.exit(1)
    
    cut_bvh_file(input_file, output_file, duration)