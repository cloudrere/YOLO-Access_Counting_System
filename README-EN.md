# Here is the complete English translation of your README, optimized for a professional GitHub repository.

# 

# \---

# 

# \# Deep Learning-Based Entry/Exit Recognition System

# 

# > A PyQt5-based entry/exit counting system powered by YOLOv8 object detection \& tracking.

# 

# A bidirectional entry/exit recognition and counting system based on \*\*PyQt5 + YOLOv8\*\*. It supports independent statistics for multiple categories, custom detection zones, real-time parameter adjustment, results export, and more.

# 

# !\[Python](https://img.shields.io/badge/Python-3.8+-blue)

# !\[PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)

# !\[YOLO](https://img.shields.io/badge/Model-YOLOv8-orange)

# !\[Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

# 

# \---

# 

# \## 📖 Table of Contents

# 

# \- \[Features](#-features)

# \- \[Project Structure](#-project-structure)

# \- \[Requirements](#-requirements)

# \- \[Installation](#-installation)

# \- \[Configuration](#-configuration)

# \- \[Quick Start](#-quick-start)

# \- \[Parameter Details](#-parameter-details)

# \- \[FAQ](#-faq)

# \- \[Development Notes](#-development-notes)

# 

# \---

# 

# \## ✨ Features

# 

# \### Core Capabilities

# 

# | Module | Description |

# |------|------|

# | 🎯 \*\*Multi-Model Support\*\* | Compatible with all YOLO series models (v5/v8/v11/v12, etc., in `.pt` format). |

# | 🚀 \*\*GPU Acceleration\*\* | Automatic detection and warmup for NVIDIA GPUs via CUDA; falls back to CPU if unavailable. |

# | 📚 \*\*YAML Class Loading\*\* | Supports loading custom class names from `data.yaml` files. |

# | ☑️ \*\*Class Filtering\*\* | Toggle specific classes to detect (e.g., Person, Car, Pet) in any combination. |

# | 🎨 \*\*Custom Detection Zones\*\* | Draw two custom polygons (Area1 \& Area2) directly on the UI to define entry/exit boundaries. |

# | 💾 \*\*Zone Persistence\*\* | Drawn zones are automatically saved to `areas.json` and reloaded on the next launch. |

# | 🔄 \*\*Hot Reloading\*\* | Adjust parameters or redraw zones during runtime; changes take effect immediately. |

# 

# \### Data Sources

# 

# \- 🎬 \*\*Video Files\*\*: MP4 / AVI / MOV / MKV

# \- 📹 \*\*Live Camera\*\*: Default device index 0

# 

# \### Parameter Adjustment (⭐ New)

# 

# | Parameter | Range | Description |

# |------|------|------|

# | \*\*Confidence Threshold\*\* | 0.05 \~ 0.95 | Filters out low-confidence detection boxes. |

# | \*\*IoU Threshold\*\* | 0.10 \~ 0.90 | Overlap threshold for Non-Maximum Suppression (NMS). |

# | \*\*Image Size\*\* | 320 \~ 1280 | Inference resolution (e.g., 640x640). |

# | \*\*Skip Frames\*\* | 1 \~ 10 | Process every Nth frame to reduce hardware load. |

# | \*\*Tracker\*\* | ByteTrack / BoT-SORT | Multi-Object Tracking (MOT) algorithm. |

# | \*\*Max Detections\*\* | 10 \~ 300 | Maximum number of objects per frame. |

# 

# \### Statistics \& Export

# 

# \- 📊 \*\*Real-time Stats\*\*: Total In, Total Out, and Current Occupancy.

# \- 📋 \*\*By-Class Stats\*\*: Independent counters for each class (e.g., Person: 3 In, Car: 2 In).

# \- 📝 \*\*Detailed Logs\*\*: Color-coded logs tracking all system operations and events.

# \- 📑 \*\*Event Table\*\*: Live log of every entry/exit event (Timestamp, ID, Class, Action).

# \- 📘 \*\*Excel Export\*\*: Includes 4 sheets (Detailed Records, Summary, By-Class Stats, Timeline).

# \- 🎞️ \*\*Video Saving\*\*: Option to save processed video with overlays (boxes, IDs, and zones).

# 

# \---

# 

# \## 📁 Project Structure

# 

# ```

# entry\_exit\_system/

# │

# ├── main.py                # Main entry point

# ├── README.md              # Project documentation

# │

# ├── ui/                    # UI Layer

# │   ├── \_\_init\_\_.py

# │   ├── main\_window.py     # Main window logic

# │   ├── dialogs.py         # Class selection dialogs

# │   ├── area\_dialog.py     # Polygon drawing dialog

# │   └── settings\_panel.py  # Parameter adjustment panel

# │

# ├── core/                  # Business Logic Layer

# │   ├── \_\_init\_\_.py

# │   ├── detector.py        # YOLO model wrapper

# │   ├── counter.py         # Multi-class entry/exit logic

# │   └── video\_thread.py    # QThread for video processing

# │

# ├── utils/                 # Utility Layer

# │   ├── \_\_init\_\_.py

# │   ├── config.py          # Config management \& Persistence

# │   ├── logger.py          # Logging utilities

# │   └── exporter.py        # Excel export logic

# │

# └── results/               # Output Directory (Auto-generated)

# &#x20;   ├── images/            # Saved detection snapshots

# &#x20;   ├── videos/            # Saved detection videos

# &#x20;   ├── excel/             # Generated Excel reports

# &#x20;   └── areas.json         # Persisted zone coordinates

# ```

# 

# \---

# 

# \## 🖥️ Requirements

# 

# \### Hardware

# \- \*\*OS\*\*: Windows 10 / 11 (Tested)

# \- \*\*GPU\*\*: NVIDIA GPU (Optional, 4GB+ VRAM recommended)

# \- \*\*CPU\*\*: Support for AVX instructions

# \- \*\*RAM\*\*: 8GB+

# 

# \### Software

# \- \*\*Python\*\*: 3.8 \~ 3.11 (3.10 recommended)

# \- \*\*CUDA\*\*: 11.8 or 12.x (Required for GPU acceleration)

# 

# \---

# 

# \## 🛠️ Installation

# 

# \### 1. Create Conda Environment (Recommended)

# 

# ```bash

# conda create -n yolo python=3.10 -y

# conda activate yolo

# ```

# 

# \### 2. Install PyTorch

# 

# \*\*GPU Version\*\* (For CUDA 11.8):

# ```bash

# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# ```

# 

# \*\*CPU Version\*\*:

# ```bash

# pip install torch torchvision

# ```

# 

# \### 3. Install Dependencies

# 

# ```bash

# pip install PyQt5 opencv-python numpy pyyaml pillow openpyxl ultralytics lapx

# ```

# 

# \### ⚠️ Critical Note

# 

# \*\*You MUST install `lapx` manually\*\* within your environment to prevent the tracker from attempting auto-installations which cause UI lag:

# 

# ```bash

# \# Use your specific Python path, e.g.:

# E:\\software\\ADeepLearning\\Anaconda\\envs\\yolo\\python.exe -m pip install lapx

# ```

# 

# \---

# 

# \## ⚙️ Configuration

# 

# \### Default Paths (`utils/config.py`)

# 

# Update these paths to match your local environment:

# 

# ```python

# class Config:

# &#x20;   # Default YOLO model path

# &#x20;   DEFAULT\_MODEL = r"E:\\DeepLearning\\YoloCode\\ultralytics-main\\weights\\yolov8n.pt"

# &#x20;   

# &#x20;   # Chinese/Unicode Font path (required for overlay labels)

# &#x20;   FONT\_PATH = r"E:\\DeepLearning\\YoloCode\\ultralytics-main\\Font\\DroidSansFallback.ttf"

# &#x20;   

# &#x20;   # Display dimensions

# &#x20;   FRAME\_WIDTH = 1020

# &#x20;   FRAME\_HEIGHT = 600

# ```

# 

# \### Local Ultralytics Path (`main.py`)

# 

# If you are using a local source code version of `ultralytics`:

# 

# ```python

# LOCAL\_ULTRALYTICS = r"E:\\DeepLearning\\YoloCode\\ultralytics-main"

# ```

# 

# \---

# 

# \## 🚀 Quick Start

# 

# \### Start the Program

# 

# ```bash

# conda activate yolo

# cd /path/to/entry\_exit\_system

# python main.py

# ```

# 

# \### Workflow

# 

# 1\.  \*\*Load Model\*\*: Automatically loads `yolov8n.pt` on startup, or use `Model → Select Model`.

# 2\.  \*\*Initialize GPU\*\*: Go to `Model → Initialize GPU` (Status bar will show `GPU Ready: NVIDIA RTX xxxx`).

# 3\.  \*\*Select Source\*\*: Click 🎬 for Video or 📹 for Camera.

# 4\.  \*\*Draw Zones (Crucial)\*\*:

# &#x20;   - Click `✏️ Draw Zones`.

# &#x20;   - \*\*Left Click\*\*: Add polygon vertex.

# &#x20;   - \*\*Right Click\*\*: Undo last point.

# &#x20;   - \*\*Radio Buttons\*\*: Switch between Area1 and Area2.

# &#x20;   - \*At least 3 points are needed for a polygon.\*

# 5\.  \*\*Logic Definition\*\*:

# &#x20;   - 🟣 \*\*Area 1 (Internal)\*\*: "Inside" the shop/room.

# &#x20;   - 🔵 \*\*Area 2 (External)\*\*: "Outside" the door.

# &#x20;   - \*\*Entry\*\*: Area 2 → Area 1 ✅

# &#x20;   - \*\*Exit\*\*: Area 1 → Area 2 ✅

# 6\.  \*\*Filter Classes\*\*: Use `Classes → Filter Classes` to select targets (e.g., Person).

# 7\.  \*\*Start\*\*: Click `▶ Start`. View real-time results in the dashboard and bottom event log.

# 

# \---

# 

# \## 🔧 Parameter Details

# 

# \### Image Size (`imgsz`)

# 

# | Size | Speed | Accuracy | Best For |

# |------|------|------|------|

# | 320 | ⚡⚡⚡⚡ | ⭐⭐ | Fast Preview |

# | 640 | ⚡⚡ | ⭐⭐⭐⭐ | \*\*Default/Balanced\*\* |

# | 1280 | 🐢 | ⭐⭐⭐⭐⭐ | Small/Distant targets |

# 

# \### Tracker

# \- \*\*ByteTrack\*\*: Default; fast and accurate for most scenarios.

# \- \*\*BoT-SORT\*\*: More robust for crowded environments but slower.

# 

# \---

# 

# \## 🐛 FAQ

# 

# \*\*Q1: UI lags or high CPU usage?\*\*

# \- Increase `Skip Frames` to 3\~5.

# \- Reduce `Image Size` to 480.

# \- Ensure GPU initialization is successful.

# 

# \*\*Q2: No counting events?\*\*

# \- Ensure the target's "Foot Point" (yellow dot) fully crosses from one polygon into the other.

# \- Check if the class is selected in filters.

# 

# \---

# 

# \## 👨‍💻 Development Notes

# 

# \### Architecture

# Uses an \*\*MVC-inspired Layered Architecture\*\*:

# \- \*\*UI Layer (`ui/`)\*\*: PyQt5 interface and event handling.

# \- \*\*Core Layer (`core/`)\*\*: YOLO inference, tracking logic, and counting state machine.

# \- \*\*Utils Layer (`utils/`)\*\*: Configuration, file I/O, and Excel exporters.

# 

# \### License

# This project is for educational and research purposes only.

# 

# \---

# 

# \*\*Enjoy counting! 🎉\*\*

