# -*- coding: utf-8 -*-
"""主窗口 - 优化布局版"""
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTextEdit, QFileDialog,
                             QMessageBox, QSplitter, QGroupBox, QGridLayout,
                             QAction, QStatusBar, QProgressBar, QTableWidget,
                             QTableWidgetItem, QHeaderView, QTabWidget,
                             QSizePolicy, QScrollArea)
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer

from core.detector import YoloDetector
from core.video_thread import DetectionThread
from ui.dialogs import ClassFilterDialog
from ui.area_dialog import AreaDrawDialog
from ui.settings_panel import SettingsPanel, DetectionSettings
from utils.config import Config
from utils.logger import logger
from utils.exporter import ExcelExporter


# ============ 全局样式 ============
GLOBAL_STYLE = """
QGroupBox {
    font-weight: bold;
    border: 1px solid #bbb;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 8px;
    background: #fafafa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
    color: #2c3e50;
}
QPushButton {
    padding: 6px;
    border-radius: 3px;
}
QLabel {
    color: #333;
}
"""


class VideoLabel(QLabel):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "background:#1a1a1a;color:#aaa;border:2px solid #333;"
            "border-radius:4px;font-size:14px;")
        self.setMinimumSize(480, 360)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setText(title)
        self._current_frame = None

    def set_frame(self, frame):
        self._current_frame = frame
        self._update_pixmap()

    def clear_frame(self, text=""):
        self._current_frame = None
        self.setText(text)

    def _update_pixmap(self):
        if self._current_frame is None:
            return
        frame = self._current_frame
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if not rgb.flags['C_CONTIGUOUS']:
            rgb = np.ascontiguousarray(rgb)
        qimg = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg).scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pix)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_pixmap()


class MainWindow(QMainWindow):

    # ⭐ 左侧固定宽度（加宽解决文字截断）
    LEFT_PANEL_WIDTH = 340

    def __init__(self):
        super().__init__()
        self.setWindowTitle("基于深度学习的进出识别系统 v1.1")
        self.resize(1800, 1000)
        self.setStyleSheet(GLOBAL_STYLE)

        self.detector = YoloDetector()
        self.thread = None
        self.source_type = None
        self.source_path = None
        self.current_stats = {}
        self.preview_frame = None

        self.settings = DetectionSettings()
        self.detector.update_params(self.settings.to_dict())

        self.area1_rel, self.area2_rel = Config.load_areas()

        logger.log_signal.connect(self.on_log)

        self._build_ui()
        self._build_menu()

        QTimer.singleShot(300, self._auto_load_default_model)

    # =================================================================
    # UI
    # =================================================================
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(6)

        left_panel = self._build_left_panel()
        left_panel.setFixedWidth(self.LEFT_PANEL_WIDTH)
        center_panel = self._build_center_panel()
        right_panel = self._build_right_panel()
        right_panel.setFixedWidth(270)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setStretchFactor(2, 0)
        main_splitter.setSizes([self.LEFT_PANEL_WIDTH, 1190, 270])

        root_layout.addWidget(main_splitter)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("就绪")

    def _build_left_panel(self):
        """左侧：滚动容器 + 所有控制面板"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.NoFrame)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # —— 模型信息 ——
        box_model = QGroupBox("模型信息")
        bm = QVBoxLayout(box_model)
        bm.setSpacing(4)
        self.lbl_model = QLabel("模型: 未加载")
        self.lbl_model.setWordWrap(True)
        self.lbl_device = QLabel("设备: 未初始化")
        self.lbl_device.setWordWrap(True)
        self.lbl_classes = QLabel("已选类别: 全部")
        self.lbl_classes.setWordWrap(True)
        for lbl in [self.lbl_model, self.lbl_device, self.lbl_classes]:
            lbl.setStyleSheet("color:#444;font-size:12px;")
        bm.addWidget(self.lbl_model)
        bm.addWidget(self.lbl_device)
        bm.addWidget(self.lbl_classes)
        layout.addWidget(box_model)

        # —— 数据源 ——
        box_src = QGroupBox("数据源")
        bs = QVBoxLayout(box_src)
        bs.setSpacing(4)
        self.btn_video = QPushButton("🎬 选择视频")
        self.btn_camera = QPushButton("📹 实时摄像头")
        self.btn_video.clicked.connect(self.on_select_video)
        self.btn_camera.clicked.connect(self.on_select_camera)
        bs.addWidget(self.btn_video)
        bs.addWidget(self.btn_camera)
        layout.addWidget(box_src)

        # —— 检测区域 ——
        box_area = QGroupBox("检测区域")
        ba = QVBoxLayout(box_area)
        ba.setSpacing(4)
        self.btn_draw_area = QPushButton("✏️ 绘制进出区域")
        self.btn_draw_area.setStyleSheet(
            "background:#9C27B0;color:white;padding:8px;font-weight:bold;border-radius:3px;")
        self.btn_reset_area = QPushButton("↺ 重置为默认区域")
        self.btn_draw_area.clicked.connect(self.on_draw_area)
        self.btn_reset_area.clicked.connect(self.on_reset_area)
        ba.addWidget(self.btn_draw_area)
        ba.addWidget(self.btn_reset_area)
        self.lbl_area_info = QLabel(
            f"区域1: {len(self.area1_rel)}点  区域2: {len(self.area2_rel)}点")
        self.lbl_area_info.setStyleSheet("color:#666;font-size:11px;")
        ba.addWidget(self.lbl_area_info)
        layout.addWidget(box_area)

        # —— ⭐ 参数调节面板 ——
        self.settings_panel = SettingsPanel(self.settings)
        self.settings_panel.settings_changed.connect(self.on_settings_changed)
        layout.addWidget(self.settings_panel)

        # —— 检测控制 ——
        box_ctrl = QGroupBox("检测控制")
        bc = QVBoxLayout(box_ctrl)
        bc.setSpacing(4)
        self.btn_start = QPushButton("▶ 开始检测")
        self.btn_pause = QPushButton("⏸ 暂停")
        self.btn_stop = QPushButton("⏹ 停止")
        self.btn_save = QPushButton("💾 保存结果")
        self.btn_start.setStyleSheet(
            "background:#4CAF50;color:white;font-weight:bold;padding:8px;border-radius:3px;")
        self.btn_pause.setStyleSheet(
            "background:#FF9800;color:white;padding:8px;border-radius:3px;")
        self.btn_stop.setStyleSheet(
            "background:#f44336;color:white;padding:8px;border-radius:3px;")
        self.btn_save.setStyleSheet(
            "background:#2196F3;color:white;padding:8px;border-radius:3px;")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_start.clicked.connect(self.on_start)
        self.btn_pause.clicked.connect(self.on_pause_resume)
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_save.clicked.connect(self.on_save)
        for b in [self.btn_start, self.btn_pause, self.btn_stop, self.btn_save]:
            bc.addWidget(b)
        layout.addWidget(box_ctrl)

        self.lbl_source = QLabel("数据源: 未选择")
        self.lbl_source.setWordWrap(True)
        self.lbl_source.setStyleSheet(
            "color:#555;padding:6px;background:#f0f0f0;border-radius:4px;font-size:11px;")
        layout.addWidget(self.lbl_source)

        layout.addStretch()

        scroll.setWidget(panel)
        return scroll

    def _build_center_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        display_widget = QWidget()
        display_layout = QVBoxLayout(display_widget)
        display_layout.setContentsMargins(0, 0, 0, 0)
        display_layout.setSpacing(2)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(4, 2, 4, 2)
        lbl_title_left = QLabel("📷 检测前（原始画面）")
        lbl_title_right = QLabel("🎯 检测后（识别结果）")
        title_style = ("color:white;background:#2c3e50;padding:6px;"
                       "font-weight:bold;font-size:13px;border-radius:3px;")
        lbl_title_left.setStyleSheet(title_style)
        lbl_title_right.setStyleSheet(title_style)
        lbl_title_left.setAlignment(Qt.AlignCenter)
        lbl_title_right.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(lbl_title_left)
        title_layout.addWidget(lbl_title_right)
        display_layout.addLayout(title_layout)

        self.view_before = VideoLabel("等待加载...")
        self.view_after = VideoLabel("等待检测...")
        video_splitter = QSplitter(Qt.Horizontal)
        video_splitter.addWidget(self.view_before)
        video_splitter.addWidget(self.view_after)
        video_splitter.setStretchFactor(0, 1)
        video_splitter.setStretchFactor(1, 1)
        video_splitter.setSizes([600, 600])
        display_layout.addWidget(video_splitter, 1)

        bottom = QWidget()
        bottom_layout = QVBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(2)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMaximumHeight(16)
        bottom_layout.addWidget(self.progress)

        self.tabs = QTabWidget()
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet(
            "background:#1e1e1e;color:#ddd;font-family:Consolas;font-size:12px;")
        self.tabs.addTab(self.log_view, "📝 运行日志")

        self.record_table = QTableWidget(0, 5)
        self.record_table.setHorizontalHeaderLabels(
            ["时间", "追踪ID", "类别", "动作", "置信度"])
        self.record_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.record_table.verticalHeader().setDefaultSectionSize(22)
        self.tabs.addTab(self.record_table, "📋 检测记录")
        bottom_layout.addWidget(self.tabs)

        v_splitter = QSplitter(Qt.Vertical)
        v_splitter.addWidget(display_widget)
        v_splitter.addWidget(bottom)
        v_splitter.setStretchFactor(0, 4)
        v_splitter.setStretchFactor(1, 1)
        v_splitter.setSizes([720, 200])

        layout.addWidget(v_splitter)
        return panel

    def _build_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(2, 2, 2, 2)

        box_stat = QGroupBox("📊 实时统计")
        bst = QGridLayout(box_stat)
        bst.setHorizontalSpacing(2)
        self.lbl_enter = QLabel("0")
        self.lbl_exit = QLabel("0")
        self.lbl_current = QLabel("0")
        for lbl in [self.lbl_enter, self.lbl_exit, self.lbl_current]:
            lbl.setAlignment(Qt.AlignCenter)
        self.lbl_enter.setStyleSheet("font-size:30px;font-weight:bold;color:#4CAF50;")
        self.lbl_exit.setStyleSheet("font-size:30px;font-weight:bold;color:#f44336;")
        self.lbl_current.setStyleSheet("font-size:30px;font-weight:bold;color:#2196F3;")
        bst.addWidget(QLabel("进入"), 0, 0, alignment=Qt.AlignCenter)
        bst.addWidget(QLabel("离开"), 0, 1, alignment=Qt.AlignCenter)
        bst.addWidget(QLabel("当前"), 0, 2, alignment=Qt.AlignCenter)
        bst.addWidget(self.lbl_enter, 1, 0)
        bst.addWidget(self.lbl_exit, 1, 1)
        bst.addWidget(self.lbl_current, 1, 2)
        layout.addWidget(box_stat)

        box_cls = QGroupBox("按类别统计")
        bcs = QVBoxLayout(box_cls)
        self.class_table = QTableWidget(0, 4)
        self.class_table.setHorizontalHeaderLabels(["类别", "进入", "离开", "当前"])
        self.class_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.class_table.verticalHeader().setDefaultSectionSize(24)
        bcs.addWidget(self.class_table)
        layout.addWidget(box_cls, 1)

        return panel

    def _build_menu(self):
        menubar = self.menuBar()

        menu_model = menubar.addMenu("模型(&M)")
        act_sel_model = QAction("选择模型", self)
        act_sel_model.triggered.connect(self.on_select_model)
        act_init = QAction("初始化GPU", self)
        act_init.triggered.connect(self.on_init_gpu)
        menu_model.addAction(act_sel_model)
        menu_model.addAction(act_init)

        menu_cls = menubar.addMenu("类别(&C)")
        act_yaml = QAction("加载YAML类别文件", self)
        act_yaml.triggered.connect(self.on_load_yaml)
        act_filter = QAction("筛选检测类别", self)
        act_filter.triggered.connect(self.on_filter_classes)
        menu_cls.addAction(act_yaml)
        menu_cls.addAction(act_filter)

        menu_area = menubar.addMenu("区域(&A)")
        act_draw = QAction("绘制进出区域", self)
        act_draw.triggered.connect(self.on_draw_area)
        act_reset = QAction("重置为默认区域", self)
        act_reset.triggered.connect(self.on_reset_area)
        menu_area.addAction(act_draw)
        menu_area.addAction(act_reset)

        menu_help = menubar.addMenu("帮助(&H)")
        act_about = QAction("关于", self)
        act_about.triggered.connect(self.on_about)
        menu_help.addAction(act_about)

    # =================================================================
    # 回调
    # =================================================================
    def on_settings_changed(self, d):
        self.detector.update_params(d)
        self.statusBar().showMessage(
            f"参数已更新: conf={d['conf']:.2f}, iou={d['iou']:.2f}, "
            f"imgsz={d['imgsz']}, skip={d['skip_frames']}", 3000)

    def _auto_load_default_model(self):
        if os.path.exists(Config.DEFAULT_MODEL):
            self._load_model(Config.DEFAULT_MODEL)
        else:
            logger.warning(f"默认模型不存在: {Config.DEFAULT_MODEL}")

    def on_select_model(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择YOLO模型", "",
            "PyTorch权重 (*.pt);;ONNX模型 (*.onnx);;所有文件 (*.*)")
        if path:
            self._load_model(path)

    def _load_model(self, path):
        ok, info = self.detector.load_model(path)
        if ok:
            self.lbl_model.setText(f"模型: {os.path.basename(path)}")
            self.statusBar().showMessage(f"模型已加载: {os.path.basename(path)}", 5000)
        else:
            QMessageBox.warning(self, "模型加载失败", str(info))

    def on_init_gpu(self):
        if self.detector.model is None:
            QMessageBox.warning(self, "提示", "请先加载模型")
            return
        ok, info = self.detector.initialize_gpu()
        self.lbl_device.setText(f"设备: {info}")
        if ok:
            QMessageBox.information(self, "初始化完成", info)

    def on_load_yaml(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择YAML类别文件", "", "YAML文件 (*.yaml *.yml)")
        if not path:
            return
        ok, info = self.detector.load_yaml(path)
        if not ok:
            QMessageBox.warning(self, "加载失败", str(info))

    def on_filter_classes(self):
        if self.detector.yaml_names:
            names = list(self.detector.yaml_names.values())
        elif self.detector.names:
            names = list(self.detector.names.values())
        else:
            QMessageBox.warning(self, "提示", "请先加载模型或YAML文件")
            return

        dlg = ClassFilterDialog(names, self.detector.selected_classes, self)
        if dlg.exec_() == dlg.Accepted:
            selected = dlg.get_selected()
            self.detector.set_selected_classes(selected)
            if selected:
                self.lbl_classes.setText(
                    f"已选类别: {', '.join(selected[:3])}" +
                    (f" 等{len(selected)}个" if len(selected) > 3 else ""))
            else:
                self.lbl_classes.setText("已选类别: 全部")

    def on_select_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择视频", "", "视频 (*.mp4 *.avi *.mov *.mkv)")
        if path:
            self.source_type = 'video'
            self.source_path = path
            # 只显示文件名，避免太长
            name = os.path.basename(path)
            if len(name) > 24:
                name = name[:22] + "..."
            self.lbl_source.setText(f"🎬 视频: {name}")
            self._preview_video_first_frame(path)
            logger.info(f"已选择视频: {path}")

    def on_select_camera(self):
        self.source_type = 'camera'
        self.source_path = 0
        self.lbl_source.setText("📹 实时摄像头: 0")
        self._preview_camera_frame()
        logger.info("已选择摄像头")

    def _preview_video_first_frame(self, path):
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.resize(frame, (Config.FRAME_WIDTH, Config.FRAME_HEIGHT))
            self.preview_frame = frame.copy()
            preview = self._draw_areas_on_frame(frame.copy())
            self.view_before.set_frame(preview)
            self.view_after.clear_frame("点击 ▶ 开始检测")

    def _preview_camera_frame(self):
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                frame = cv2.resize(frame, (Config.FRAME_WIDTH, Config.FRAME_HEIGHT))
                self.preview_frame = frame.copy()
                preview = self._draw_areas_on_frame(frame.copy())
                self.view_before.set_frame(preview)
                self.view_after.clear_frame("点击 ▶ 开始检测")
                return
        self.view_before.clear_frame("摄像头预览失败\n可直接开始检测")
        self.view_after.clear_frame("等待检测...")

    def _draw_areas_on_frame(self, frame):
        h, w = frame.shape[:2]
        a1 = Config.rel_to_abs(self.area1_rel, w, h)
        a2 = Config.rel_to_abs(self.area2_rel, w, h)
        if len(a1) >= 3:
            overlay = frame.copy()
            cv2.fillPoly(overlay, [np.array(a1, np.int32)], (255, 0, 255))
            cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
            cv2.polylines(frame, [np.array(a1, np.int32)], True, (255, 0, 255), 2)
        if len(a2) >= 3:
            overlay = frame.copy()
            cv2.fillPoly(overlay, [np.array(a2, np.int32)], (0, 220, 255))
            cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
            cv2.polylines(frame, [np.array(a2, np.int32)], True, (0, 220, 255), 2)
        return frame

    def on_draw_area(self):
        if self.preview_frame is None:
            QMessageBox.warning(self, "提示",
                                "请先选择视频或摄像头，以便在画面上绘制区域！")
            return
        dlg = AreaDrawDialog(self.preview_frame,
                             self.area1_rel, self.area2_rel, self)
        if dlg.exec_() == dlg.Accepted:
            a1, a2 = dlg.get_areas()
            self.area1_rel = a1
            self.area2_rel = a2
            Config.save_areas(a1, a2)
            self.lbl_area_info.setText(
                f"区域1: {len(a1)}点  区域2: {len(a2)}点")
            if self.thread and self.thread.isRunning():
                self.thread.update_areas(a1, a2)
                logger.info("区域已热更新")
            preview = self._draw_areas_on_frame(self.preview_frame.copy())
            self.view_before.set_frame(preview)
            logger.success("进出区域已更新并保存")

    def on_reset_area(self):
        ret = QMessageBox.question(
            self, "重置", "确定恢复为默认区域吗？",
            QMessageBox.Yes | QMessageBox.No)
        if ret != QMessageBox.Yes:
            return
        self.area1_rel = list(Config.DEFAULT_AREA1_REL)
        self.area2_rel = list(Config.DEFAULT_AREA2_REL)
        Config.save_areas(self.area1_rel, self.area2_rel)
        self.lbl_area_info.setText(
            f"区域1: {len(self.area1_rel)}点  区域2: {len(self.area2_rel)}点")
        if self.preview_frame is not None:
            preview = self._draw_areas_on_frame(self.preview_frame.copy())
            self.view_before.set_frame(preview)
        logger.info("区域已重置为默认")

    def on_start(self):
        if self.detector.model is None:
            QMessageBox.warning(self, "提示", "请先加载模型")
            return
        if self.source_type is None:
            QMessageBox.warning(self, "提示", "请先选择数据源")
            return
        if self.thread and self.thread.isRunning():
            QMessageBox.information(self, "提示", "检测已在运行")
            return

        self.record_table.setRowCount(0)
        self.detector.update_params(self.settings.to_dict())

        self.thread = DetectionThread(
            detector=self.detector,
            source_type=self.source_type,
            source_path=self.source_path,
            area1_rel=self.area1_rel,
            area2_rel=self.area2_rel,
            settings=self.settings
        )
        self.thread.frame_ready.connect(self.on_frame)
        self.thread.stats_updated.connect(self.on_stats)
        self.thread.detection_event.connect(self.on_record)
        self.thread.finished_signal.connect(self.on_thread_finished)
        self.thread.progress_signal.connect(self.on_progress)
        self.thread.start()

        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.progress.setVisible(True)
        logger.success(
            f"开始检测 (conf={self.settings.conf:.2f}, "
            f"iou={self.settings.iou:.2f}, imgsz={self.settings.imgsz})")

    def on_pause_resume(self):
        if not self.thread:
            return
        if self.btn_pause.text() == "⏸ 暂停":
            self.thread.pause()
            self.btn_pause.setText("▶ 继续")
            logger.info("已暂停")
        else:
            self.thread.resume()
            self.btn_pause.setText("⏸ 暂停")
            logger.info("已继续")

    def on_stop(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait(2000)
            if self.thread.records:
                ret = QMessageBox.question(
                    self, "保存结果",
                    f"本次共检测到 {len(self.thread.records)} 条进出记录，是否导出Excel？",
                    QMessageBox.Yes | QMessageBox.No)
                if ret == QMessageBox.Yes:
                    self._do_export()
        self.on_thread_finished()

    def on_thread_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_pause.setText("⏸ 暂停")
        self.progress.setVisible(False)
        logger.info("检测结束")

    def on_save(self):
        if self.thread is None or not self.thread.records:
            QMessageBox.information(self, "提示", "暂无检测记录可保存")
            return
        self.thread.set_save_enabled(True)
        self._do_export()
        QMessageBox.information(
            self, "已开启保存",
            f"检测帧和视频将保存到:\n{Config.VIDEO_DIR}\n{Config.IMAGE_DIR}")

    def _do_export(self):
        if self.thread is None:
            return
        ok, info = ExcelExporter.export(self.thread.records, self.current_stats)
        if ok:
            QMessageBox.information(self, "导出成功", f"Excel已保存:\n{info}")
        else:
            QMessageBox.warning(self, "导出失败", str(info))

    def on_frame(self, raw, processed):
        raw_with_areas = self._draw_areas_on_frame(raw.copy())
        self.view_before.set_frame(raw_with_areas)
        self.view_after.set_frame(processed)

    def on_stats(self, stats):
        self.current_stats = stats
        self.lbl_enter.setText(str(stats['total_enter']))
        self.lbl_exit.setText(str(stats['total_exit']))
        self.lbl_current.setText(str(stats['current']))

        by_class = stats.get('by_class', {})
        self.class_table.setRowCount(len(by_class))
        for i, (cname, s) in enumerate(by_class.items()):
            self.class_table.setItem(i, 0, QTableWidgetItem(cname))
            self.class_table.setItem(i, 1, QTableWidgetItem(str(s['enter'])))
            self.class_table.setItem(i, 2, QTableWidgetItem(str(s['exit'])))
            self.class_table.setItem(i, 3, QTableWidgetItem(str(s['current'])))

    def on_record(self, rec):
        row = self.record_table.rowCount()
        self.record_table.insertRow(row)
        self.record_table.setItem(row, 0, QTableWidgetItem(rec['time']))
        self.record_table.setItem(row, 1, QTableWidgetItem(str(rec['track_id'])))
        self.record_table.setItem(row, 2, QTableWidgetItem(rec['class']))
        item = QTableWidgetItem(rec['action'])
        if rec['action'] == '进入':
            item.setForeground(QColor('#4CAF50'))
        else:
            item.setForeground(QColor('#f44336'))
        self.record_table.setItem(row, 3, item)
        self.record_table.setItem(row, 4, QTableWidgetItem(str(rec['confidence'])))
        self.record_table.scrollToBottom()

    def on_progress(self, cur, total):
        if total > 0:
            self.progress.setMaximum(total)
            self.progress.setValue(cur)

    def on_log(self, level, msg):
        color_map = {"INFO": "#8be9fd", "WARNING": "#f1fa8c",
                     "ERROR": "#ff5555", "SUCCESS": "#50fa7b"}
        color = color_map.get(level, "#ffffff")
        self.log_view.append(f'<span style="color:{color}">{msg}</span>')

    def on_about(self):
        QMessageBox.about(
            self, "关于",
            "基于深度学习的进出识别系统 v1.1\n\n"
            "• YOLOv8 目标检测与追踪\n"
            "• 多类别独立进出计数\n"
            "• 自定义检测区域\n"
            "• 置信度/IoU等参数实时调节\n"
            "• 结果导出Excel")

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait(2000)
        event.accept()
