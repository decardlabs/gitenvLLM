python -m venv venv      # 创建
source venv/bin/activate # 激活（Linux/Mac）
deactivate               # 退出
pip list                 # 看装了什么包
pip freeze > requirements.txt  # 导出依赖
pip install -r requirements.txt # 安装依赖