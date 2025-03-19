import re
import json
from datetime import datetime

def parse_timestamp(line):
    # 匹配时间戳格式 [YYMMDD HH:MM:SS.NNNNNN]
    match = re.search(r'\[(\d{6})\s+(\d{2}:\d{2}:\d{2}\.\d+)\]', line)
    if match:
        date_str, time_str = match.groups()
        year = 2000 + int(date_str[:2])
        month = int(date_str[2:4])
        day = int(date_str[4:6])
        
        # 解析时间部分
        time_obj = datetime.strptime(time_str, '%H:%M:%S.%f')
        
        # 组合完整的datetime对象
        full_datetime = datetime(year, month, day,
                               time_obj.hour, time_obj.minute, time_obj.second,
                               time_obj.microsecond)
        
        # 转换为时间戳
        timestamp = full_datetime.timestamp()
        return timestamp, full_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
    return None, None

def parse_obstacle_line(line):
    # 解析障碍物信息，支持负数 ID
    pattern = r'obs id\s*:\s*(-?\d+).*start_t\s*:\s*(\d+\.\d+).*end_t\s*(\d+\.\d+).*start _l_s\s*:\s*(\d+\.\d+).*end_l_s\s*:\s*(\d+\.\d+).*start_up_s\s*:\s*(\d+\.\d+).*end_u_s\s*:\s*(\d+\.\d+)'
    match = re.search(pattern, line)
    if match:
        obs_id, start_t, end_t, start_l_s, end_l_s, start_up_s, end_up_s = match.groups()
        return {
            "id": int(obs_id),  # 将字符串转换为整数，支持负数
            "start_low_s": float(start_l_s),
            "start_up_s": float(start_up_s),
            "end_low_s": float(end_l_s),
            "end_up_s": float(end_up_s),
            "start_t": float(start_t),
            "end_t": float(end_t)
        }
    return None

def parse_trajectory_line(line):
    # 解析轨迹信息行
    match = re.search(r't\s*:\s*(\d+\.\d+).*s\s*:\s*(\d+\.\d+)', line)
    if match:
        t, s = map(float, match.groups())
        return {"t": t, "s": s}
    return None

def process_keylog_to_json():
    with open('../data/keylogs.txt', 'r') as f:
        lines = f.readlines()
    result = []
    current_frame = None
    current_trajectories = []
    
    try:
        with open('../data/output.json', 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            if "Iter Deduction Complete obs list" in line:
                if current_frame:
                    if current_trajectories:  # 只有在有轨迹数据时才添加
                        current_frame["trajectories"] = current_trajectories
                    result.append(current_frame)
                
                timestamp, timestamp_readable = parse_timestamp(line)
                current_frame = {
                    "timestamp": timestamp,
                    "timestamp_readable": timestamp_readable,
                    "obstacles": []
                }
                current_trajectories = []
                
            elif current_frame and "obs id" in line:
                obstacle = parse_obstacle_line(line)
                if obstacle:
                    current_frame["obstacles"].append(obstacle)
                    
            elif "Iter deduction result" in line:
                trajectory = parse_trajectory_line(line)
                if trajectory:
                    current_trajectories.append(trajectory)
        
        # 保存最后一帧
        if current_frame:
            if current_trajectories:  # 只有在有轨迹数据时才添加
                current_frame["trajectories"] = current_trajectories
            result.append(current_frame)
        
        # 写入JSON文件
        with open('output.json', 'w') as f:
            json.dump(result, f, indent=2)
            
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {keylog_path}")
        raise
    except Exception as e:
        print(f"处理过程中出现错误：{str(e)}")
        raise

if __name__ == "__main__":
    process_keylog_to_json()