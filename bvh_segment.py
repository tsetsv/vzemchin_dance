import os

def split_bvh_with_data_folder(input_file, segments, output_folder='data'):
    """
    BVH файлыг segment-үүдэд тасалж 'data' folder-т хадгалах
    
    Parameters:
    -----------
    input_file : str
        Эх BVH файлын нэр
    segments : list of tuples
        [(start, end, name), ...] жагсаалт
    output_folder : str
        Хадгалах folder-ын нэр (default: 'data')
    """
    
    # Data folder үүсгэх
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Folder үүсгэсэн: {output_folder}/")
    
    # BVH файл унших
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # HIERARCHY хэсгийг олох
    motion_index = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('MOTION'):
            motion_index = i
            break
    
    # Header хэсэг (HIERARCHY + MOTION declaration)
    header = lines[:motion_index + 1]
    
    # Frame Time мөр
    frame_time_line = lines[motion_index + 2]
    frame_time = float(frame_time_line.split(':')[1].strip())
    fps = 1.0 / frame_time
    
    # Motion data хэсэг
    motion_start_index = motion_index + 3
    motion_data = lines[motion_start_index:]
    
    print(f"\n📊 Эх файл: {input_file}")
    print(f"   Нийт frames: {len(motion_data)}")
    print(f"   FPS: {fps:.2f}")
    print(f"   Frame Time: {frame_time:.6f}")
    print(f"\n{'#':<4} {'Нэр':<20} {'Start':<8} {'End':<8} {'Frames':<8} {'Секунд':<10}")
    print("=" * 70)
    
    # Segment бүрийг боловсруулах
    success_count = 0
    for idx, (start, end, name) in enumerate(segments, 1):
        # Frame индекс (1-based → 0-based)
        start_idx = start - 1
        end_idx = end - 1
        
        # Хязгаар шалгах
        if start_idx < 0:
            print(f"⚠️  [{idx}] {name}: Start frame хэт бага ({start})")
            continue
        
        if end_idx >= len(motion_data):
            print(f"⚠️  [{idx}] {name}: End frame хэт их ({end} > {len(motion_data)})")
            continue
        
        if start_idx >= end_idx:
            print(f"⚠️  [{idx}] {name}: Start >= End ({start} >= {end})")
            continue
        
        # Segment өгөгдөл авах
        segment_data = motion_data[start_idx:end_idx + 1]
        num_frames = len(segment_data)
        duration = num_frames * frame_time
        
        # Шинэ файл бичих
        output_file = os.path.join(output_folder, f"{name}.bvh")
        
        with open(output_file, 'w') as f:
            # Header бичих
            f.writelines(header)
            
            # Frames тоо
            f.write(f"Frames: {num_frames}\n")
            
            # Frame Time
            f.write(frame_time_line)
            
            # Motion data
            f.writelines(segment_data)
        
        success_count += 1
        print(f"✅ [{idx}] {name:<20} {start:<8} {end:<8} {num_frames:<8} {duration:<10.2f}")
    
    print("=" * 70)
    print(f"🎉 Амжилттай: {success_count}/{len(segments)} segment хадгалагдлаа")
    print(f"📂 Байршил: {output_folder}/\n")


# ===== ТАНЫ ӨГӨГДӨЛ =====

segments = [
    # (start, end, name)
    (515, 995, 'vdolgion_2x1'),
    (1175, 1595, 'vdolgion_2x2'),
    (1737, 2173, 'vdolgion_2x3'),
    (2248, 2676, 'vdolgion_2x4'),
    (3185, 3669, 'vdolgion_2x5'),
    (3824, 4275, 'vdolgion_2x6'),
    (4324, 4709, 'vdolgion_2x7'),
    (4922, 5303, 'vshiijih_2x1'),
    (5455, 5887, 'vshiijih_2x2'),
    (6124, 6500, 'vshiijih_2x3'),
    (6860, 7335, 'vshiijih_2x4'),
    (7386, 7740, 'vshiijih_2x5'),
    (7878, 8251, 'vshiijih_2x6'),
    (8495, 9000, 'vnuman_2x1'),
    (9153, 9697, 'vnuman_2x2'),
    (9725, 10259, 'vnuman_2x3'),
    (10340, 10851, 'vnuman_2x4'),
    (10928, 11454, 'vnuman_2x5'),
    (11446, 11938, 'vnuman_2x6'),
]

# Функц дуудах
split_bvh_with_data_folder('shot2.bvh', segments, output_folder='data')