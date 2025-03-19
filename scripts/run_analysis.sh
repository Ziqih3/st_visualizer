#!/bin/bash

# 定义退出函数
exit_script() {
    echo -e "\n退出脚本..."
    exit 0
}

# 设置 ESC 键的 trap
trap exit_script $'\e'

echo "ST图日志分析工具 - 自动处理脚本"
echo "============================"
echo "按 ESC 键可随时退出"

echo "步骤 1: 提取日志数据"
python ../tools/log_cut.py
if [ $? -ne 0 ]; then
    echo "日志提取失败！"
    exit 1
fi
echo "日志提取完成。"

echo
echo "步骤 2: 转换为JSON格式"
python ../tools/keylog2json.py
if [ $? -ne 0 ]; then
    echo "JSON转换失败！"
    exit 1
fi
echo "JSON转换完成。"

echo
echo "步骤 3: 启动ST图可视化工具"
echo "启动可视化工具，关闭窗口或按 ESC 键退出..."
python ../tools/st_viewer.py
if [ $? -ne 0 ]; then
    echo "可视化工具启动失败！"
    exit 1
fi

