# -*- coding: utf-8 -*-
"""
主程序入口 - 基于深度学习的进出识别系统
"""
import sys
import os

# ============================================================
# 关键环境变量配置 —— 必须在 import ultralytics 之前设置
# ============================================================
# 1. 禁用 ultralytics 每次启动的依赖自动检查/安装（解决卡顿）
os.environ['YOLO_AUTOINSTALL'] = 'False'
# 2. 禁用在线检查
os.environ['YOLO_OFFLINE'] = 'True'
# 3. 禁用使用统计上报
os.environ['YOLO_ANALYTICS'] = 'False'

# ============================================================
# 使用本地 ultralytics 源码
# ============================================================
LOCAL_ULTRALYTICS = r"E:\DeepLearning\YOLO-Access_Counting_System\ultralytics-main"
if os.path.isdir(LOCAL_ULTRALYTICS) and LOCAL_ULTRALYTICS not in sys.path:
    sys.path.insert(0, LOCAL_ULTRALYTICS)

# 验证加载路径
try:
    import ultralytics
    print(f"[INFO] ultralytics 路径: {ultralytics.__file__}")
except Exception as e:
    print(f"[ERROR] ultralytics 导入失败: {e}")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.main_window import MainWindow


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 9))

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
