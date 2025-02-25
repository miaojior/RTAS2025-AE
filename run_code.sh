#!/bin/bash

# 进入 conda 环境
source ~/anaconda3/etc/profile.d/conda.sh  # 可能需要调整路径
conda activate rtas

# 进入 Python 脚本所在目录（如果不在同一目录）
cd /home/rtas/rtas  # 替换为实际目录

# 运行 Python 脚本
python main.py