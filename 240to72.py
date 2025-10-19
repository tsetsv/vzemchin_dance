def resample_bvh(input_file, output_file, original_fps=240, target_fps=72):
    """
    BVH файлын FPS-ийг өөрчлөх
    240 fps → 72 fps гэвэл 240/72 = 3.33 дахь бүр frame авна
    """
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # HIERARCHY хэсгийг олох
    motion_index = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('MOTION'):
            motion_index = i
            break
    
    # Header хэсэг (HIERARCHY + MOTION мэдээлэл)
    header = lines[:motion_index + 3]  # MOTION, Frames, Frame Time хүртэл
    
    # Frame Time өөрчлөх
    frame_time = 1.0 / target_fps
    header[-1] = f'Frame Time: {frame_time:.6f}\n'
    
    # Motion data хэсэг
    motion_data = lines[motion_index + 3:]
    
    # Resample ratio
    ratio = original_fps / target_fps  # 240/72 = 3.333...
    
    # Шинэ frame-үүд сонгох
    new_frames = []
    frame_indices = []
    
    for i in range(len(motion_data)):
        target_frame = i * ratio
        if target_frame < len(motion_data):
            frame_indices.append(int(round(target_frame)))
    
    # Давхардсан index арилгах
    frame_indices = sorted(list(set(frame_indices)))
    
    # Frame-үүдийг сонгох
    for idx in frame_indices:
        if idx < len(motion_data):
            new_frames.append(motion_data[idx])
    
    # Шинэ frame тоог засах
    header[-2] = f'Frames: {len(new_frames)}\n'
    
    # Файл бичих
    with open(output_file, 'w') as f:
        f.writelines(header)
        f.writelines(new_frames)
    
    print(f"✅ Амжилттай!")
    print(f"   Эхний frames: {len(motion_data)}")
    print(f"   Шинэ frames: {len(new_frames)}")
    print(f"   Эхний FPS: {original_fps}")
    print(f"   Шинэ FPS: {target_fps}")
    print(f"   Эхний үргэлжлэх хугацаа: {len(motion_data)/original_fps:.2f}s")
    print(f"   Шинэ үргэлжлэх хугацаа: {len(new_frames)/target_fps:.2f}s")

# ХЭРЭГЛЭХ:
resample_bvh('shot1_004_Skeleton_002.bvh', 'shot3.bvh', 
             original_fps=240, target_fps=72)