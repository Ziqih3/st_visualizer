import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import QDateTime
from float_sider import FloatSlider
from bisect import bisect_left
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False     # 用来正常显示负号

class STViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ST图可视化工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建matplotlib图形
        self.figure = Figure(figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.highlighted_info = None  # 添加新属性存储高亮信息
        self.highlighted_pos = None   # 添加新属性存储标注位置

        # 创建文本显示区域
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setMaximumHeight(200)
        
        # 创建时间滑块
        self.slider = FloatSlider()
        
        # 添加部件到布局
        layout.addWidget(self.canvas)
        layout.addWidget(self.text_display)
        layout.addWidget(self.slider)
        
        # 加载数据
        self.load_data()
        
        # 连接信号
        self.slider.valueChanged.connect(self.on_slider_value_changed)  # 添加新的信号连接
        self.slider.timeChanged.connect(self.update_display)
        
        # 颜色映射字典
        self.color_map = {}
        self.colors = plt.cm.tab20(np.linspace(0, 1, 20))  # 20种不同的颜色
        self.color_index = 0
        
        # 添加点击事件和高亮ID
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.highlighted_id = None
        
        # 添加键盘事件处理
        self.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QKeyEvent
        
        if event.type() == event.KeyPress:
            if isinstance(event, QKeyEvent):
                if event.key() == Qt.Key_Escape:
                    self.close()
                    return True
        return super().eventFilter(obj, event)
    
    def get_obstacle_color(self, obs_id):
        if obs_id not in self.color_map:
            self.color_map[obs_id] = self.colors[self.color_index % len(self.colors)]
            self.color_index += 1
        return self.color_map[obs_id]
    
    def on_slider_value_changed(self, value):
        # 在滑块值改变时清除高亮信息
        self.highlighted_id = None
        self.highlighted_info = None
        self.highlighted_pos = None
    
    def update_display(self, current_time):
        if not hasattr(self, 'data') or not self.data:
            return
            
        # 移除这里的清除高亮信息代码
        frame = self.find_nearest_frame(current_time)
        
        # 清除之前的图形
        self.ax.clear()
        
        # 计算当前帧中所有障碍物的最大纵向距离
        max_s = 0
        for obs in frame['obstacles']:
            max_s = max(max_s, obs['start_up_s'], obs['end_up_s'])
        
        # 设置坐标轴标签和范围
        self.ax.set_xlabel('预测时间 t (s)')
        self.ax.set_ylabel('纵向距离 s (m)')
        self.ax.set_title(f'ST图 - {frame["timestamp_readable"]}')
        self.ax.set_ylim(bottom=0, top=max_s * 1.1)  # 留出10%的余量
        
        # 添加网格线
        self.ax.grid(True, linestyle='--', alpha=0.3)
        
        # 记录已显示的ID
        displayed_ids = set()
        
        # 绘制每个障碍物的上下边界
        for obs in frame['obstacles']:
            color = self.get_obstacle_color(obs['id'])
            t = [obs['start_t'], obs['end_t']]
            
            # 根据是否高亮调整透明度和线宽
            is_highlighted = obs['id'] == self.highlighted_id
            alpha = 0.8 if is_highlighted else 0.2
            line_width = 3 if is_highlighted else 1
            
            # 绘制上下边界
            s_upper = [obs['start_up_s'], obs['end_up_s']]
            s_lower = [obs['start_low_s'], obs['end_low_s']]
            self.ax.plot(t, s_upper, color=color, linestyle='-', linewidth=line_width)
            self.ax.plot(t, s_lower, color=color, linestyle='--', linewidth=line_width)
            
            # 只有当ID未显示过时才显示标签
            if obs['id'] not in displayed_ids:
                self.ax.text(obs['start_t'], obs['start_up_s'], f'ID {obs["id"]}', 
                            color=color, 
                            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'),
                            ha='left', va='bottom')
                displayed_ids.add(obs['id'])
            
            # 填充上下边界之间的区域
            self.ax.fill_between(t, s_lower, s_upper, color=color, alpha=alpha)
        
        # 绘制轨迹线
        if 'trajectories' in frame:
            t_points = [point['t'] for point in frame['trajectories']]
            s_points = [point['s'] for point in frame['trajectories']]
            self.ax.plot(t_points, s_points, 'r-', linewidth=2, label='规划轨迹')
        
        # 不再需要图例
        # self.ax.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc='lower left',
        #               mode="expand", ncol=5, borderaxespad=0)
        
        # 调整布局参数
        self.figure.tight_layout(rect=[0, 0, 0.95, 0.95])
        
        # 更新画布
        self.canvas.draw()
        
        # 如果有高亮信息，重新显示标注
        if self.highlighted_info and self.highlighted_pos:
            self.ax.annotate(self.highlighted_info,
                xy=self.highlighted_pos,
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                fontsize=8,
                zorder=1000)
            self.canvas.draw()
        
        # 更新文本显示
        display_text = f"时间戳: {frame['timestamp_readable']}\n\n"
        display_text += "障碍物列表:\n"
        for obs in frame['obstacles']:
            display_text += f"\n障碍物 ID: {obs['id']}\n"
            display_text += f"纵向位置: {obs['start_low_s']:.3f} -> {obs['end_low_s']:.3f}\n"
            display_text += f"预测时间: {obs['start_t']:.3f} -> {obs['end_t']:.3f}\n"
            display_text += f"速度范围: {obs['start_up_s']:.3f} -> {obs['end_up_s']:.3f}\n"
            display_text += "-" * 40 + "\n"
            
        self.text_display.setText(display_text)

    def load_data(self):
        try:
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(script_dir, '..', 'data', 'output.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
                
            if not self.data:
                self.text_display.setText("没有数据")
                return
                
            # 提取所有时间戳
            self.timestamps = [frame['timestamp'] for frame in self.data]
            
            # 设置滑块的时间范围
            start_time = QDateTime.fromSecsSinceEpoch(int(min(self.timestamps)))
            end_time = QDateTime.fromSecsSinceEpoch(int(max(self.timestamps)))
            self.slider.set_time_range(start_time, end_time)
            
        except FileNotFoundError:
            self.text_display.setText("找不到 output.json 文件")
        except json.JSONDecodeError:
            self.text_display.setText("JSON 文件格式错误")
            
    def find_nearest_frame(self, target_time):
        """使用二分查找找到最接近目标时间的帧"""
        timestamp = target_time.toSecsSinceEpoch() + target_time.time().msec() / 1000.0
        pos = bisect_left(self.timestamps, timestamp)
        
        if pos == 0:
            return self.data[0]
        if pos == len(self.timestamps):
            return self.data[-1]
            
        # 比较前后两个时间戳，返回更接近的
        before = self.timestamps[pos - 1]
        after = self.timestamps[pos]
        if abs(timestamp - before) < abs(timestamp - after):
            return self.data[pos - 1]
        return self.data[pos]

    def on_click(self, event):
        if not event.inaxes:
            return
            
        current_time = self.slider.get_current_time()
        frame = self.find_nearest_frame(current_time)
        
        # 存储所有包含点击位置的障碍物
        clicked_obstacles = []
        
        for obs in frame['obstacles']:
            # 计算障碍物的四个顶点
            vertices = [
                (obs['start_t'], obs['start_low_s']),  # 左下
                (obs['start_t'], obs['start_up_s']),   # 左上
                (obs['end_t'], obs['end_up_s']),       # 右上
                (obs['end_t'], obs['end_low_s'])       # 右下
            ]
            
            # 检查点击位置是否在障碍物区域内（考虑斜率）
            if (obs['start_t'] <= event.xdata <= obs['end_t']):
                # 计算点击位置对应的上下边界值
                t_ratio = (event.xdata - obs['start_t']) / (obs['end_t'] - obs['start_t'])
                s_lower = obs['start_low_s'] + (obs['end_low_s'] - obs['start_low_s']) * t_ratio
                s_upper = obs['start_up_s'] + (obs['end_up_s'] - obs['start_up_s']) * t_ratio
                
                # 严格检查点击位置是否在上下边界之间
                if s_lower <= event.ydata <= s_upper:
                    area = (obs['end_t'] - obs['start_t']) * (obs['start_up_s'] - obs['start_low_s'])
                    clicked_obstacles.append((obs, area))
        
        if clicked_obstacles:
            clicked_obs = min(clicked_obstacles, key=lambda x: x[1])[0]
            
            if self.highlighted_id == clicked_obs['id']:
                self.highlighted_id = None
                self.highlighted_info = None
                self.highlighted_pos = None
            else:
                self.highlighted_id = clicked_obs['id']
                # 计算平均速度
                time_diff = clicked_obs['end_t'] - clicked_obs['start_t']
                avg_speed = (clicked_obs['end_low_s'] - clicked_obs['start_low_s']) / time_diff if time_diff != 0 else 0
                
                # 显示障碍物详细信息
                self.highlighted_info = (
                    f"障碍物详细信息:\n"
                    f"ID: {clicked_obs['id']}\n"
                    f"纵向位置: {clicked_obs['start_low_s']:.2f}m -> {clicked_obs['end_low_s']:.2f}m\n"
                    f"平均速度: {avg_speed:.2f}m/s\n"
                    f"预测时间: {clicked_obs['start_t']:.2f}s -> {clicked_obs['end_t']:.2f}s\n"
                    f"面积: {(clicked_obs['end_t'] - clicked_obs['start_t']) * (clicked_obs['start_up_s'] - clicked_obs['start_low_s']):.2f}m·s\n"
                )
                self.highlighted_pos = (event.xdata, event.ydata)
            
            self.update_display(current_time)
        else:
            if self.highlighted_id is not None:
                self.highlighted_id = None
                self.highlighted_info = None
                self.highlighted_pos = None
                self.update_display(current_time)

def main():
    app = QApplication(sys.argv)
    viewer = STViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()