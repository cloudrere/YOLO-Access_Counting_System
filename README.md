# 基于深度学习的进出识别系统

中文版

> A PyQt5-based entry/exit counting system powered by YOLOv8 object detection & tracking.

基于 **PyQt5 + YOLOv8** 的进出识别与双向计数系统，支持多类别独立统计、自定义检测区域、实时参数调节、结果导出等功能。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)
![YOLO](https://img.shields.io/badge/Model-YOLOv8-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

<img width="400" alt="主界面" src="https://github.com/user-attachments/assets/5f28244c-91a8-460f-b992-b13f20d6da80" />
<img width="400" alt="类别筛选" src="https://github.com/user-attachments/assets/fe3f5606-986b-496a-b0c3-04137d95a518" />
<img width="400" alt="自定义开始离开区域" src="https://github.com/user-attachments/assets/587f856f-1f98-4648-be0b-06c2d9c376a4" />
<img width="400" alt="跟踪计数" src="https://github.com/user-attachments/assets/87aaa5ce-0f99-4639-9b5f-dac393f2317a" />


## 📖 目录

- [功能特性](#-功能特性)
- [项目结构](#-项目结构)
- [环境要求](#-环境要求)
- [安装指南](#-安装指南)
- [配置说明](#-配置说明)
- [使用教程](#-使用教程)
- [参数详解](#-参数详解)
- [常见问题](#-常见问题)
- [开发说明](#-开发说明)

---

## ✨ 功能特性

### 核心功能

| 模块 | 说明 |
|------|------|
| 🎯 **多模型支持** | 兼容所有 YOLO 系列模型（v5/v8/v11/v12 等 `.pt` 格式） |
| 🚀 **GPU加速** | 自动检测并预热GPU，支持 CUDA，也可降级到 CPU |
| 📚 **YAML类别加载** | 支持加载 `data.yaml` 文件自定义类别名称 |
| ☑️ **类别筛选** | 勾选想要检测的类别，支持多选（人、车、宠物等任意组合） |
| 🎨 **自定义检测区域** | 鼠标在画面上绘制两个进出判定多边形区域 |
| 💾 **区域持久化** | 绘制的区域自动保存，下次启动自动加载 |
| 🔄 **运行时热更新** | 检测过程中调整参数或区域，立即生效 |

### 数据源

- 🎬 **视频文件**：MP4 / AVI / MOV / MKV
- 📹 **实时摄像头**：默认使用设备 0

### 参数调节（⭐ 新增）

| 参数 | 范围 | 说明 |
|------|------|------|
| **置信度阈值** | 0.05 ~ 0.95 | 过滤低置信度检测框 |
| **IoU阈值** | 0.10 ~ 0.90 | NMS重叠阈值 |
| **图像尺寸** | 320 / 480 / 640 / 768 / 960 / 1280 | 推理分辨率 |
| **跳帧间隔** | 1 ~ 10 | 每N帧处理1次，用于降低负载 |
| **追踪器** | ByteTrack / BoT-SORT | 多目标追踪算法 |
| **最大检测数** | 10 ~ 300 | 单帧最大目标数 |

### 统计与导出

- 📊 **实时统计**：总进入、总离开、当前在场
- 📋 **按类别统计**：每个类别独立统计（例如：人进了3个，车进了2个）
- 📝 **详细日志**：彩色日志显示所有操作与事件
- 📑 **检测记录表**：每条进出事件的时间、ID、类别、动作
- 📘 **Excel导出**：4个工作表（记录、总体统计、按类别统计、时间线）
- 🎞️ **视频保存**：可选择保存检测后视频（带检测框与区域叠加）

---

## 📁 项目结构

```
entry_exit_system/
│
├── main.py                       # 主程序入口
├── README.md                     # 本文档
│
├── ui/                           # 界面层
│   ├── __init__.py
│   ├── main_window.py            # 主窗口
│   ├── dialogs.py                # 类别筛选对话框
│   ├── area_dialog.py            # 区域绘制对话框
│   └── settings_panel.py         # 参数调节面板
│
├── core/                         # 业务逻辑层
│   ├── __init__.py
│   ├── detector.py               # YOLO检测器封装
│   ├── counter.py                # 多类别进出计数器
│   └── video_thread.py           # 视频处理子线程
│
├── utils/                        # 工具层
│   ├── __init__.py
│   ├── config.py                 # 配置管理 + 区域持久化
│   ├── logger.py                 # 日志工具
│   └── exporter.py               # Excel导出
│
└── results/                      # 运行产物（自动生成）
    ├── images/                   # 保存的检测图片
    ├── videos/                   # 保存的检测视频
    ├── excel/                    # Excel统计文件
    └── areas.json                # 区域配置（自动）
```

---

## 🖥️ 环境要求

### 硬件

- **操作系统**：Windows 10 / 11（已测试）
- **显卡**：NVIDIA GPU（可选，建议 4GB+ 显存）
- **CPU**：支持 AVX 指令集即可
- **内存**：8GB+

### 软件

- **Python**：3.8 ~ 3.11（推荐 3.10）
- **CUDA**：11.8 或 12.x（可选，仅GPU时需要）

---

## 🛠️ 安装指南

### 1. 创建 Conda 环境（推荐）

```bash
conda create -n yolo python=3.10 -y
conda activate yolo
```

### 2. 安装 PyTorch

**GPU 版本**（推荐，需CUDA 11.8）：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**CPU 版本**：
```bash
pip install torch torchvision
```

### 3. 安装其他依赖

```bash
pip install PyQt5 opencv-python numpy pyyaml pillow openpyxl ultralytics lapx
```

### ⚠️ 关键提示

**必须在当前 Python 环境中安装 `lapx`**（追踪器依赖），否则程序会反复尝试自动安装造成卡顿：

```bash
# 使用你的Python环境路径，例如：
E:\software\ADeepLearning\Anaconda\envs\yolo\python.exe -m pip install lapx
```

---

## ⚙️ 配置说明

### 修改默认路径 (`utils/config.py`)

根据你的实际路径修改：

```python
class Config:
    # 默认YOLO模型路径
    DEFAULT_MODEL = r"E:\DeepLearning\YoloCode\ultralytics-main\weights\yolov8n.pt"
    
    # 中文字体路径（必须存在，用于防止中文乱码）
    FONT_PATH = r"E:\DeepLearning\YoloCode\ultralytics-main\Font\DroidSansFallback.ttf"
    
    # 视频显示尺寸
    FRAME_WIDTH = 1020
    FRAME_HEIGHT = 600
```

### 修改 ultralytics 源码路径 (`main.py`)

如果使用本地源码：

```python
LOCAL_ULTRALYTICS = r"E:\DeepLearning\YoloCode\ultralytics-main"
```

---

## 🚀 使用教程

### 启动程序

```bash
conda activate yolo
cd /path/to/entry_exit_system
python main.py
```

启动后会看到控制台输出：
```
[INFO] ultralytics 路径: E:\DeepLearning\YoloCode\ultralytics-main\ultralytics\__init__.py
```

### 完整工作流程

#### ① 加载模型
- 启动时自动加载默认模型（`yolov8n.pt`）
- 或通过菜单 `模型 → 选择模型` 加载其他模型

#### ② 初始化GPU（可选）
- 菜单 `模型 → 初始化GPU`
- 检测到GPU时状态栏显示 `GPU就绪: NVIDIA RTX xxxx`

#### ③ 选择数据源
- **视频**：点击 🎬 选择视频
- **摄像头**：点击 📹 实时摄像头
- 选择后左侧立即显示**首帧预览**，叠加显示当前检测区域

#### ④ 绘制进出区域（核心）
- 点击 `✏️ 绘制进出区域`
- 在弹出窗口中：
  - **左键**：添加多边形顶点
  - **右键**：撤销上一点
  - **单选框**：切换 Area1 / Area2
  - **至少3个点** 才能构成多边形

**区域含义：**
- 🟣 **Area1（内侧）**：进入的终点 / 离开的起点（店内侧）
- 🔵 **Area2（外侧）**：进入的起点 / 离开的终点（店门外）

**判定逻辑：**
```
目标从 Area2 → Area1 = 进入 ✅
目标从 Area1 → Area2 = 离开 ✅
```

#### ⑤ 筛选检测类别
- 菜单 `类别 → 筛选检测类别`
- 勾选想要检测的类别（人、车、猫、狗等可任意组合）
- 不勾选默认为全部类别

#### ⑥ 调节参数（左侧参数面板）
- 室内光线好：`conf=0.4` + `iou=0.5`
- 远距离小目标：`imgsz=1280`
- 卡顿：`skip_frames=3` 或更高
- 实时监控：`tracker=ByteTrack`
- 密集人群：`tracker=BoT-SORT`

#### ⑦ 开始检测
- 点击 `▶ 开始检测`
- 实时查看：
  - 左侧画面：原始+区域叠加
  - 右侧画面：检测框+追踪ID+脚点
  - 右侧面板：实时统计+按类别统计
  - 底部记录：每条进出事件

**检测框颜色含义：**
- 🔴 红色：普通目标
- 🔵 青色：已进入外侧区域（Area2）
- 🟣 紫色：已进入内侧区域（Area1）
- 🟢 绿色：已计入"进入"统计

#### ⑧ 暂停/继续/停止
- ⏸ 暂停：保留状态，可继续
- ⏹ 停止：结束检测，弹窗询问是否导出Excel

#### ⑨ 保存结果
- 点击 `💾 保存结果`：立即导出Excel + 后续帧自动保存
- 停止时选择"是"：仅导出Excel

---

## 🔧 参数详解

### 置信度阈值 (conf)

控制多严格地过滤检测框：

| 值 | 效果 |
|----|------|
| 0.15 | 非常宽松，可能误检 |
| 0.25 | **默认推荐**，平衡 |
| 0.50 | 严格，仅保留高质量检测 |
| 0.70+ | 非常严格，可能漏检 |

### IoU阈值 (iou)

NMS（非极大值抑制）时，用于判定两个检测框是否是同一目标：

| 值 | 效果 |
|----|------|
| 0.30 | 严格去重，密集目标可能被合并 |
| 0.45 | **默认推荐** |
| 0.60 | 宽松，允许更多重叠框 |

### 图像尺寸 (imgsz)

| 尺寸 | 速度 | 精度 | 适用 |
|------|------|------|------|
| 320 | ⚡⚡⚡⚡ | ⭐⭐ | 快速预览 |
| 480 | ⚡⚡⚡ | ⭐⭐⭐ | CPU推理 |
| 640 | ⚡⚡ | ⭐⭐⭐⭐ | **默认推荐** |
| 960 | ⚡ | ⭐⭐⭐⭐⭐ | 需要高精度 |
| 1280 | 🐢 | ⭐⭐⭐⭐⭐ | 远距离小目标 |

### 跳帧间隔 (skip_frames)

- `1`：每帧都处理（最流畅）
- `2`：**默认**，每2帧处理1次
- `5`：每5帧处理1次（大幅减轻卡顿，但追踪可能丢失）
- `10`：仅作快速浏览

### 追踪器

- **ByteTrack**：默认，速度快，精度高，适合大多数场景
- **BoT-SORT**：对密集人群更鲁棒，但速度稍慢

---

## 🐛 常见问题

### Q1: 启动时报 `Ultralytics requirement ['lapx>=0.5.2'] not found`

**原因**：当前Python环境未安装 `lapx`

**解决**：
```bash
E:\software\ADeepLearning\Anaconda\envs\yolo\python.exe -m pip install lapx
```

### Q2: 界面卡顿、CPU占用很高

**尝试**：
1. 将 `跳帧间隔` 调到 3~5
2. 将 `图像尺寸` 调到 480
3. 确认已启用GPU（菜单 → 模型 → 初始化GPU）
4. 检查是否在反复触发 AutoUpdate（见Q1）

### Q3: 检测不到目标/漏检很多

**尝试**：
1. 降低 `置信度阈值` 到 0.15~0.20
2. 增大 `图像尺寸` 到 960/1280
3. 检查类别筛选是否勾选了目标类别
4. 使用更大的模型（如 `yolov8m.pt` / `yolov8l.pt`）

### Q4: 进出没有计数

**检查清单**：
- [ ] 区域是否正确绘制（至少3个点）
- [ ] 目标脚点（黄色圆点）是否真的穿过了两个区域
- [ ] 类别筛选里是否勾选了该目标的类别
- [ ] 目标是否有稳定的追踪ID（看检测框左上角 `ID:X`）

### Q5: 中文显示乱码

**原因**：字体文件路径错误

**解决**：检查 `utils/config.py` 中的 `FONT_PATH` 是否存在

### Q6: 摄像头无法打开

**尝试**：
1. 确认其他程序（如钉钉/腾讯会议）未占用摄像头
2. 修改 `main_window.py` 的 `on_select_camera` 中 `self.source_path = 0` 为 `1` 或 `2`

### Q7: Excel 导出后数据乱

**原因**：不同检测会话共享了记录

**解决**：点击 `▶ 开始检测` 会自动清空上一次的记录

---

## 👨‍💻 开发说明

### 架构设计

采用 **MVC 分层架构**：

```
┌─────────────────────────────┐
│       UI Layer (ui/)        │  PyQt5 界面
├─────────────────────────────┤
│    Core Layer (core/)       │  YOLO检测、计数、线程
├─────────────────────────────┤
│    Utils Layer (utils/)     │  配置、日志、导出
└─────────────────────────────┘
```

### 关键类

- `YoloDetector` (`core/detector.py`)：封装YOLO模型加载、推理、追踪
- `EntryExitCounter` (`core/counter.py`)：状态机实现进出判定，按类别独立计数
- `DetectionThread` (`core/video_thread.py`)：QThread子线程处理视频流
- `DetectionSettings` (`ui/settings_panel.py`)：参数容器
- `MainWindow` (`ui/main_window.py`)：主窗口协调各模块

### 扩展方向

想要继续增强，可以考虑：

1. **RTSP/RTMP 流支持**：在 `video_thread.py` 中 `cv2.VideoCapture("rtsp://...")`
2. **多摄像头**：拓展 `source_path` 列表，创建多个 `DetectionThread`
3. **数据库存储**：将 `records` 写入 SQLite/MySQL 替代 Excel
4. **报警功能**：当某类进入数超过阈值时触发声音/邮件
5. **年龄性别识别**：在检测到 `person` 后接入分类模型
6. **热力图**：累计所有脚点绘制密度热图

### 许可证

本项目仅供学习研究使用。

---

## 📞 联系方式
获取源码请加微信（备注来意，有偿服务）
<img width="1268" height="1729" alt="wechat" src="https://github.com/user-attachments/assets/e577994d-a4c6-4c3e-a44a-b4f167ae5e76" />
- 项目问题：提交 Issue
- 技术交流：欢迎 PR

---

**Enjoy counting! 🎉**
