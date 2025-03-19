## Directory Structure
st_visualizer/  
├── tools/  
│   ├── log_cut.py        # 日志提取工具  
│   ├── keylog2json.py    # JSON转换工具  
│   └── st_viewer.py      # ST图可视化工具  
├── scripts/  
│   └── run_analysis.sh   # 自动处理脚本  
├── data/  
│   ├── log              # 输入日志文件  
│   ├── keylogs.txt      # 提取的关键日志  
│   └── output.json      # 转换后的JSON数据  
└── README.md            # 项目说明文档  


# ST图日志分析工具

这是一个用于分析和可视化 ST 图数据的工具集。该工具集包含三个主要组件，可以单独使用或通过脚本一键运行。

## 快速开始
1. 将原始日志文件重命名为 `log` 并放在data目录下
2. 运行自动处理脚本：
```bash
bash run_analysis.sh
```

## 使用步骤

### 1. 日志提取 (log_cut.py)
首先使用 `log_cut.py` 从原始日志中提取相关数据：
```bash
python log_cut.py
```
- 输入：原始日志文件 `log` 将原始log文件改名为‘log’
- 输出：提取后的关键日志 `keylogs.txt`
- 功能：提取包含 "Iter Deduction Complete obs list" 或 "Iter deduction result" 的相关数据行

### 2. JSON转换 (keylog2json.py)
接下来使用 `keylog2json.py` 将提取的日志转换为结构化的 JSON 格式：
```bash
python keylog2json.py
```
- 输入：`keylogs.txt`
- 输出：`output.json`
- 功能：解析日志中的时间戳和障碍物信息，转换为标准 JSON 格式

### 3. ST图可视化 (st_viewer.py)
最后使用 `st_viewer.py` 进行可视化显示：
```bash
python st_viewer.py
```
- 输入：`output.json`
- 功能：
  - 显示交互式 ST 图
  - 时间轴滑块控制
  - 障碍物区域颜色区分
  - 点击ID 标签下区域高亮

## 数据格式说明

### 输入日志格式
原始日志需要包含以下信息：
- 时间戳格式：`[YYMMDD HH:MM:SS.NNNNNN]`
- 障碍物信息行：包含 obs id、start_t、end_t 等字段

### JSON数据结构
```json
[
  {
    "timestamp": 1741598228.128002,
    "timestamp_readable": "2025-03-10 17:17:08.128002",
    "obstacles": [
      {
        "id": 17123,
        "start_low_s": 27.4,
        "start_up_s": 88.8,
        "end_low_s": 27.4,
        "end_up_s": 88.8,
        "start_t": 0.0,
        "end_t": 8.0
      }
    ],
    "trajectories": [
      {
        "t": 0.0,
        "s": 30.0
      }
    ]
  }
]
```
## 界面说明
1. 主视图区域：显示 ST 图
   
   - 横轴：预测时间 t (s)
   - 纵轴：纵向距离 s (m)
   - 彩色区域：障碍物预测范围
   - 红色实线：规划轨迹（如果存在）
2. 时间滑块：
   - 用于选择查看的时间点
   - 可拖动或点击调整
3. 信息面板：
   - 显示当前时间戳
   - 列出所有障碍物的详细信息

## 依赖项
```bash
pip install PyQt5 matplotlib numpy
```

## debug
1. 按照顺序运行这三个工具
2. 每个工具都会检查必要的输入文件是否存在
3. 运行 st_viewer.py 时会自动处理中文显示
