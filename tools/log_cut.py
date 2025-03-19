import re

def extract_obs_data(log_file_path):
    found_target = False
    with open('../data/keylogs.txt', 'w') as output_file:
        with open(log_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # 查找目标行
                if "Iter Deduction Complete obs list" in line or "Iter deduction result" in line:
                    found_target = True
                    output_file.write(line.strip() + '\n')
                    continue
                
                if found_target:
                    # 使用更简单的正则表达式
                    if "obs id" in line and "start_t" in line and "end_t" in line:
                        output_file.write(line.strip() + '\n')
                    else:
                        if line.strip():  # 如果不是空行，才重置标记
                            found_target = False

if __name__ == "__main__":
    log_file_path = "../data/log"
    try:
        extract_obs_data(log_file_path)
        print("处理完成，请查看 keylogs.txt 文件")
    except Exception as e:
        print(f"发生错误：{str(e)}")