import os
import sys
import json

# Setup Local Engine Paths for libmpv & FFmpeg
search_paths = []

# PyInstaller temporary extraction folder
if hasattr(sys, '_MEIPASS'):
    search_paths.append(sys._MEIPASS)
    search_paths.append(os.path.join(sys._MEIPASS, "engine"))

# Executable directory
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    search_paths.append(exe_dir)
    search_paths.append(os.path.join(exe_dir, "engine"))

# Source script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
search_paths.append(script_dir)
search_paths.append(os.path.join(script_dir, "engine"))

# Inject search paths into PATH and add_dll_directory for Windows
for p in search_paths:
    if p and os.path.exists(p):
        os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(p)
            except Exception:
                pass

# Locate FFMPEG and FFPROBE binaries
FFMPEG_BIN = "ffmpeg"
FFPROBE_BIN = "ffprobe"

for p in search_paths:
    ff_candidate = os.path.join(p, "ffmpeg.exe")
    fp_candidate = os.path.join(p, "ffprobe.exe")
    if os.path.exists(ff_candidate):
        FFMPEG_BIN = ff_candidate
        break

for p in search_paths:
    fp_candidate = os.path.join(p, "ffprobe.exe")
    if os.path.exists(fp_candidate):
        FFPROBE_BIN = fp_candidate
        break

import mpv
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# ==========================================================================
# CUSTOM STYLING (QSS) THEME SYSTEM
# ==========================================================================

ACCENT_COLORS = {
    "violet": "#8b5cf6",
    "cyan": "#06b6d4",
    "emerald": "#10b981",
    "rose": "#f43f5e",
    "amber": "#f59e0b"
}

ACCENT_HOVERS = {
    "violet": "#7c3aed",
    "cyan": "#0891b2",
    "emerald": "#059669",
    "rose": "#e11d48",
    "amber": "#d97706"
}

def get_theme_qss(theme_name, accent_name):
    accent_hex = ACCENT_COLORS.get(accent_name, "#8b5cf6")
    accent_hover = ACCENT_HOVERS.get(accent_name, "#7c3aed")
    
    if theme_name == "obsidian":
        bg_app = "#060913"
        bg_panel = "#0d111c"
        bg_card = "#161c2d"
        text_main = "#f1f5f9"
        text_sec = "#94a3b8"
        border_light = "rgba(255, 255, 255, 0.08)"
    elif theme_name == "cyberpunk":
        bg_app = "#05000a"
        bg_panel = "#120121"
        bg_card = "#24033e"
        text_main = "#fdf2f8"
        text_sec = "#f472b6"
        border_light = "rgba(244, 63, 94, 0.15)"
    elif theme_name == "frost":
        bg_app = "#cbd5e1"
        bg_panel = "#f1f5f9"
        bg_card = "#ffffff"
        text_main = "#0f172a"
        text_sec = "#475569"
        border_light = "rgba(15, 23, 42, 0.15)"
    else:  # light
        bg_app = "#f1f5f9"
        bg_panel = "#ffffff"
        bg_card = "#e2e8f0"
        text_main = "#0f172a"
        text_sec = "#475569"
        border_light = "rgba(0, 0, 0, 0.08)"

    if theme_name in ("frost", "light"):
        disabled_bg = "rgba(0, 0, 0, 0.05)"
        disabled_text = "rgba(15, 23, 42, 0.4)"
        remux_disabled_bg = "rgba(245, 158, 11, 0.4)"
    else:
        disabled_bg = "rgba(255, 255, 255, 0.03)"
        disabled_text = "rgba(255, 255, 255, 0.3)"
        remux_disabled_bg = "rgba(245, 158, 11, 0.3)"

    return f"""
    QMainWindow {{
        background-color: {bg_app};
        color: {text_main};
    }}
    QWidget#main_widget {{
        background-color: {bg_app};
        color: {text_main};
    }}
    QFrame#titlebar {{
        background-color: {bg_app};
        border-bottom: 1px solid {border_light};
    }}
    QLabel#title_label {{
        color: {text_sec};
        font-family: 'Segoe UI', sans-serif;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 0.5px;
    }}
    QFrame#sidebar {{
        background-color: {bg_panel};
        border-left: 1px solid {border_light};
    }}
    QTabWidget::panel {{
        border: none;
        background-color: {bg_panel};
    }}
    QTabBar::tab {{
        background: transparent;
        color: {text_sec};
        padding: 10px 14px;
        font-size: 11px;
        font-weight: bold;
        border: none;
    }}
    QTabBar::tab:selected {{
        color: {accent_hex};
        border-bottom: 2px solid {accent_hex};
    }}
    QListWidget {{
        background-color: {bg_card};
        border: 1px solid {border_light};
        border-radius: 8px;
        color: {text_main};
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 8px;
        border-radius: 4px;
    }}
    QListWidget::item:hover {{
        background-color: rgba(255, 255, 255, 0.05);
    }}
    QListWidget::item:selected {{
        background-color: {accent_hex};
        color: #ffffff;
    }}
    QPushButton {{
        background-color: {bg_card};
        border: 1px solid {border_light};
        border-radius: 6px;
        color: {text_main};
        padding: 5px 10px;
        font-size: 11px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {accent_hex};
        border-color: {accent_hex};
        color: #ffffff;
    }}
    QPushButton:disabled {{
        background-color: {disabled_bg};
        color: {disabled_text};
        border-color: {border_light};
    }}
    QPushButton#remux_btn {{
        background-color: #f59e0b;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    QPushButton#remux_btn:hover {{
        background-color: #d97706;
        border-color: #d97706;
    }}
    QPushButton#remux_btn:disabled {{
        background-color: {remux_disabled_bg};
        color: {disabled_text};
        border-color: transparent;
    }}
    QPushButton#mirror_btn:checked {{
        background-color: {accent_hex};
        border-color: {accent_hex};
        color: #ffffff;
    }}
    QPushButton#mirror_btn:checked:hover {{
        background-color: {accent_hover};
        border-color: {accent_hover};
    }}
    QPushButton[rebinding="true"] {{
        background-color: {accent_hex};
        color: #ffffff;
        border-color: {accent_hex};
    }}
    QPushButton[rebinding="true"]:hover {{
        background-color: {accent_hover};
        border-color: {accent_hover};
    }}
    
    /* Titlebar Buttons Specific Styling */
    QPushButton#titlebar_btn {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 0px;
        color: {text_sec};
    }}
    QPushButton#titlebar_btn:hover {{
        background-color: rgba(255, 255, 255, 0.12);
        color: {text_main};
        border: none;
    }}
    QPushButton#titlebar_close_btn {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 0px;
        color: {text_sec};
    }}
    QPushButton#titlebar_close_btn:hover {{
        background-color: #ef4444;
        color: #ffffff;
        border: none;
    }}
    
    /* Playback Control Row Buttons Specific Styling */
    QFrame#controls_panel QPushButton {{
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 0px;
        color: {text_sec};
    }}
    QFrame#controls_panel QPushButton:hover {{
        background-color: rgba(255, 255, 255, 0.08);
        color: {text_main};
        border: none;
    }}
    QFrame#controls_panel QPushButton#play_btn {{
        background-color: transparent;
        color: {text_sec};
        border-radius: 6px;
    }}
    QFrame#controls_panel QPushButton#play_btn:hover {{
        background-color: rgba(255, 255, 255, 0.08);
        color: {text_main};
    }}
    QFrame#controls_panel QPushButton#shuffle_btn[active="true"] {{
        background-color: {accent_hex};
        color: #ffffff;
        border-radius: 4px;
    }}
    QFrame#controls_panel QPushButton#shuffle_btn[active="true"]:hover {{
        background-color: {accent_hover};
    }}
    QFrame#controls_panel QPushButton#repeat_btn[repeat_mode="all"] {{
        background-color: {accent_hex};
        color: #ffffff;
        border-radius: 4px;
    }}
    QFrame#controls_panel QPushButton#repeat_btn[repeat_mode="all"]:hover {{
        background-color: {accent_hover};
    }}
    QFrame#controls_panel QPushButton#repeat_btn[repeat_mode="one"] {{
        background-color: {accent_hex};
        color: #ffffff;
        border-radius: 4px;
    }}
    QFrame#controls_panel QPushButton#repeat_btn[repeat_mode="one"]:hover {{
        background-color: {accent_hover};
    }}
    QFrame#controls_panel QPushButton#ab_btn_active {{
        background-color: {accent_hex};
        color: #ffffff;
        border: 1px solid {accent_hex};
        border-radius: 6px;
    }}
    QFrame#controls_panel QPushButton#ab_btn_active:hover {{
        background-color: {accent_hover};
        border-color: {accent_hover};
        color: #ffffff;
        border: 1px solid {accent_hover};
    }}
    
    QSlider::groove:horizontal {{
        height: 6px;
        background: {bg_card};
        border-radius: 3px;
    }}
    QSlider::sub-page:horizontal {{
        background: {accent_hex};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: #ffffff;
        border: 1px solid {border_light};
        width: 12px;
        height: 12px;
        margin: -3px 0;
        border-radius: 6px;
    }}
    QSlider::groove:vertical {{
        width: 6px;
        background: {bg_card};
        border-radius: 3px;
    }}
    QSlider::handle:vertical {{
        background: #ffffff;
        border: 1px solid {border_light};
        width: 12px;
        height: 12px;
        margin: 0 -3px;
        border-radius: 6px;
    }}
    QSlider::add-page:vertical {{
        background: {accent_hex};
        border-radius: 3px;
    }}
    QLineEdit {{
        background-color: {bg_card};
        border: 1px solid {border_light};
        border-radius: 6px;
        color: {text_main};
        padding: 6px;
    }}
    QCheckBox {{
        color: {text_main};
        font-size: 11px;
    }}
    QComboBox {{
        background-color: {bg_card};
        border: 1px solid {border_light};
        border-radius: 6px;
        color: {text_main};
        padding: 4px 8px;
    }}
    QLabel {{
        color: {text_main};
    }}
    QGroupBox {{
        color: {text_sec};
        font-weight: bold;
        border: 1px solid {border_light};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 12px;
    }}
    """

# ==========================================================================
# CUSTOM WIDGETS
# ==========================================================================

class ABLoopSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.ab_start = None
        self.ab_end = None
        self.ab_active = False

    def set_ab_loop(self, start, end, active):
        self.ab_start = start
        self.ab_end = end
        self.ab_active = active
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.maximum() <= 0:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width = self.width()
        
        if self.ab_start is not None:
            # Draw Start Marker (A)
            start_px = int((self.ab_start / self.maximum()) * width)
            painter.setPen(QPen(QColor("#06b6d4"), 2))
            painter.setBrush(QBrush(QColor("#06b6d4")))
            painter.drawRect(start_px - 2, 0, 4, self.height())
            
            # Draw Label A above
            painter.setPen(QColor("#ffffff"))
            painter.setFont(QFont("Arial", 7, QFont.Weight.Bold))
            painter.drawText(start_px - 4, 10, "A")
            
            if self.ab_end is not None:
                # Draw End Marker (B)
                end_px = int((self.ab_end / self.maximum()) * width)
                painter.setPen(QPen(QColor("#06b6d4"), 2))
                painter.drawRect(end_px - 2, 0, 4, self.height())
                
                # Draw Label B above
                painter.setPen(QColor("#ffffff"))
                painter.drawText(end_px - 4, 10, "B")
                
                # Draw highlight region
                if self.ab_active:
                    painter.fillRect(start_px, 2, end_px - start_px, self.height() - 4, QColor(6, 182, 212, 50))
        painter.end()


class DragDropListWidget(QListWidget):
    file_dropped = Signal(str)
    order_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

    def keyboardSearch(self, search):
        # Disable default keyboard search to prevent conflict with global hotkeys
        pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        # Scan folder recursively for media files
                        video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.ts', '.mp3', '.wav', '.flac')
                        try:
                            for root, dirs, files in os.walk(file_path):
                                for f in sorted(files):
                                    if f.lower().endswith(video_extensions):
                                        self.file_dropped.emit(os.path.join(root, f))
                        except Exception as e:
                            print("Failed to scan dropped folder:", e)
                    elif file_path.lower().endswith(
                        ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.ts', '.mp3', '.wav', '.flac')
                    ):
                        self.file_dropped.emit(file_path)
        else:
            super().dropEvent(event)
            self.order_changed.emit()


class LibraryListWidget(QListWidget):
    def keyboardSearch(self, search):
        # Disable default keyboard search to prevent conflict with global hotkeys
        pass


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def get_video_thumbnail_static(video_path):
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        
    cache_dir = os.path.join(app_dir, ".thumbnails")
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir)
        except Exception:
            pass
            
    import hashlib
    path_hash = hashlib.md5(video_path.encode('utf-8')).hexdigest()
    thumb_path = os.path.join(cache_dir, f"{path_hash}.png")
    
    if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
        return thumb_path
        
    try:
        import subprocess
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        cmd = [FFMPEG_BIN, "-y", "-ss", "00:00:02", "-i", video_path, "-vframes", "1", "-vf", "scale=160:90", thumb_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creation_flags, timeout=5)
        if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
            return thumb_path
    except Exception as e:
        print("Failed to extract thumbnail via FFmpeg:", e)
        
    return None

class ThumbnailSignals(QObject):
    finished = Signal(str, str)

class ThumbnailWorker(QRunnable):
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.signals = ThumbnailSignals()

    def run(self):
        try:
            thumb_path = get_video_thumbnail_static(self.video_path)
            if thumb_path:
                self.signals.finished.emit(self.video_path, thumb_path)
        except Exception as e:
            print("Error in thumbnail worker:", e)


# ==========================================================================
# MAIN APPLICATION WINDOW
# ==========================================================================

DEFAULT_HOTKEYS = {
    "play_pause": {"label": "Play / Pause", "key": "Space"},
    "mute": {"label": "Mute / Unmute", "key": "M"},
    "fullscreen": {"label": "Toggle Fullscreen", "key": "F"},
    "seek_back": {"label": "Seek Back 5s", "key": "Left"},
    "seek_fwd": {"label": "Seek Forward 5s", "key": "Right"},
    "volume_up": {"label": "Volume Up", "key": "Up"},
    "volume_down": {"label": "Volume Down", "key": "Down"},
    "next_video": {"label": "Next Video", "key": "N"},
    "prev_video": {"label": "Previous Video", "key": "Shift+N"},
    "ab_loop": {"label": "A-B Loop Mark", "key": "A"},
}

class BingeBoxPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # State settings
        self.playlist = []
        self.current_index = -1
        self.repeat_mode = "off" # off, one, all
        self.shuffle_enabled = False
        
        self.theme = "obsidian"
        self.accent = "violet"
        self.night_mode = False
        self.normalizer = False
        self.controls_theme = "semi_transparent"
        
        self.thread_pool = QThreadPool.globalInstance()
        self.scanned_folder = ""
        self.bookmarks = {}
        
        # Controls hide timer for fullscreen auto-hide
        self.controls_hide_timer = QTimer(self)
        self.controls_hide_timer.setInterval(2000) # 2 seconds
        self.controls_hide_timer.setSingleShot(True)
        self.controls_hide_timer.timeout.connect(self.hide_controls_in_fullscreen)
        
        self.ab_start = None
        self.ab_end = None
        self.ab_active = False
        
        # Video transform states
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.rotation_angle = 0
        self.mirror_enabled = False
        
        # Audio enhancer states
        self.night_mode = False
        self.normalizer = False
        self.audio_delay = 0.0 # seconds
        self.eq_bands = [0.0] * 10
        self.preamp = 0.0
        
        # Keybindings state
        self.hotkeys = DEFAULT_HOTKEYS.copy()
        self.rebinding_action = None
        
        # Load local storage if exists
        self.load_settings()
        
        # Set Window Icon
        icon_path = get_resource_path("bingebox_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        # Frameless window configuration variables
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._drag_pos = None
        
        # Initialize mpv Engine
        self.mpv_player = None
        self.eq_bands = [0, 0, 0, 0, 0]
        self.preamp = 0
        
        # Build layout UI
        self.init_ui()
        self.apply_theme()
        
        # Load playlist files into list widget
        self.populate_playlist_list()
        
        # Rescan folder library if preset folder is configured
        if getattr(self, "scanned_folder", ""):
            self.rescan_library()
            
        if self.playlist:
            self.load_video(0)
            
        # Draw dynamic shortcuts list
        self.update_shortcuts_ui()
        
        # Set up playback timers
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_playback_progress)
        
        # Install global event filter for keyboard shortcuts stability
        QCoreApplication.instance().installEventFilter(self)

    def load_settings(self):
        # Read from local folder
        try:
            settings_file = "bingebox_settings.json"
            if not os.path.exists(settings_file) and os.path.exists("aether_settings.json"):
                settings_file = "aether_settings.json"
                
            if os.path.exists(settings_file):
                with open(settings_file, "r") as f:
                    data = json.load(f)
                    self.playlist = data.get("playlist", [])
                    self.theme = data.get("theme", "obsidian")
                    self.accent = data.get("accent", "violet")
                    self.night_mode = data.get("night_mode", False)
                    self.normalizer = data.get("normalizer", False)
                    self.scanned_folder = data.get("scanned_folder", "")
                    self.bookmarks = data.get("bookmarks", {})
                    self.controls_theme = data.get("controls_theme", "semi_transparent")
                    
                    # Merge loaded hotkeys to handle backwards compatibility
                    saved_hotkeys = data.get("hotkeys", {})
                    for act, conf in DEFAULT_HOTKEYS.items():
                        if act in saved_hotkeys:
                            self.hotkeys[act]["key"] = saved_hotkeys[act]["key"]
        except Exception as e:
            print("Failed to load settings:", e)

    def save_settings(self):
        try:
            with open("bingebox_settings.json", "w") as f:
                json.dump({
                    "playlist": self.playlist,
                    "theme": self.theme,
                    "accent": self.accent,
                    "night_mode": self.night_mode,
                    "normalizer": self.normalizer,
                    "hotkeys": self.hotkeys,
                    "scanned_folder": getattr(self, "scanned_folder", ""),
                    "bookmarks": getattr(self, "bookmarks", {}),
                    "controls_theme": getattr(self, "controls_theme", "semi_transparent")
                }, f)
        except Exception as e:
            print("Failed to save settings:", e)

    def request_thumbnail(self, video_path, item):
        # 1. Set default icon first
        item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        
        # 2. Check if already cached on disk
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
            
        cache_dir = os.path.join(app_dir, ".thumbnails")
        import hashlib
        path_hash = hashlib.md5(video_path.encode('utf-8')).hexdigest()
        thumb_path = os.path.join(cache_dir, f"{path_hash}.png")
        
        if os.path.exists(thumb_path):
            item.setIcon(QIcon(thumb_path))
            return
            
        # 3. If not cached, fetch in background thread
        worker = ThumbnailWorker(video_path)
        
        def on_finished(v_path, t_path):
            # Update icons for all matching items in playlist
            for i in range(self.playlist_list.count()):
                li = self.playlist_list.item(i)
                if li.data(Qt.ItemDataRole.UserRole) == v_path:
                    li.setIcon(QIcon(t_path))
            # and in library
            for i in range(self.library_list.count()):
                li = self.library_list.item(i)
                if li.data(Qt.ItemDataRole.UserRole) == v_path:
                    li.setIcon(QIcon(t_path))
                    
        worker.signals.finished.connect(on_finished)
        self.thread_pool.start(worker)

    def init_ui(self):
        # Central Main Widget
        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("main_widget")
        self.setCentralWidget(self.main_widget)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Custom Title Bar Layout
        self.titlebar = QFrame(self.main_widget)
        self.titlebar.setObjectName("titlebar")
        self.titlebar.setFixedHeight(34)
        titlebar_layout = QHBoxLayout(self.titlebar)
        titlebar_layout.setContentsMargins(12, 0, 6, 0)
        titlebar_layout.setSpacing(10)
        
        # App brand logo icon text/image
        logo_label = QLabel(self.titlebar)
        logo_pixmap = QPixmap(get_resource_path("bingebox_icon.ico"))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("🎬")
            logo_label.setStyleSheet("font-size: 15px;")
        titlebar_layout.addWidget(logo_label)
        
        title_label = QLabel("BingeBox", self.titlebar)
        title_label.setObjectName("title_label")
        titlebar_layout.addWidget(title_label)
        
        titlebar_layout.addStretch()
        
        # Window buttons
        min_btn = QPushButton("⎯", self.titlebar)
        min_btn.setObjectName("titlebar_btn")
        min_btn.setFixedSize(28, 22)
        min_btn.clicked.connect(self.showMinimized)
        titlebar_layout.addWidget(min_btn)
        
        max_btn = QPushButton("⬜", self.titlebar)
        max_btn.setObjectName("titlebar_btn")
        max_btn.setFixedSize(28, 22)
        max_btn.clicked.connect(self.toggle_maximize)
        titlebar_layout.addWidget(max_btn)
        
        close_btn = QPushButton("✕", self.titlebar)
        close_btn.setObjectName("titlebar_close_btn")
        close_btn.setFixedSize(28, 22)
        close_btn.clicked.connect(self.close)
        titlebar_layout.addWidget(close_btn)
        
        self.main_layout.addWidget(self.titlebar)
        
        # Drag mechanics bindings
        self.titlebar.mousePressEvent = self.titlebar_press
        self.titlebar.mouseMoveEvent = self.titlebar_move
        self.titlebar.mouseDoubleClickEvent = self.titlebar_double_click
        
        # 2. Main Area Layout
        content_widget = QWidget(self.main_widget)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Video Section (Left)
        self.video_area = QWidget(content_widget)
        self.video_area_layout = QVBoxLayout(self.video_area)
        self.video_area_layout.setContentsMargins(0, 0, 0, 0)
        self.video_area_layout.setSpacing(0)
        
        # Outer Frame clipping video geometry translations
        self.video_container = QWidget(self.video_area)
        self.video_container.setStyleSheet("background-color: #000000;")
        self.video_container.resizeEvent = self.video_container_resized
        
        self.video_frame = QFrame(self.video_container)
        self.video_frame.setStyleSheet("background-color: #000000;")
        
        # Enable mouse tracking for fullscreen controls detection
        self.setMouseTracking(True)
        self.main_widget.setMouseTracking(True)
        self.video_container.setMouseTracking(True)
        self.video_frame.setMouseTracking(True)
        
        # Initialize mpv player and attach renderer to video_frame window handle
        try:
            self.mpv_player = mpv.MPV(
                wid=str(int(self.video_frame.winId())),
                vo="gpu",
                hwdec="auto-safe",
                keep_open=True,
                volume=80,
                mute=False
            )
        except Exception as e:
            print("Fallback mpv initialization:", e)
            self.mpv_player = mpv.MPV(
                wid=str(int(self.video_frame.winId())),
                keep_open=True,
                volume=80,
                mute=False
            )
        
        self.video_area_layout.addWidget(self.video_container, 1)
        
        # Bottom Player Controls Row
        self.controls_panel = QFrame(self.video_area)
        self.controls_panel.setMouseTracking(True)
        self.controls_panel.setObjectName("controls_panel")
        self.controls_panel.setFixedHeight(75)
        self.apply_controls_theme()
        controls_layout = QVBoxLayout(self.controls_panel)
        controls_layout.setContentsMargins(16, 8, 16, 8)
        controls_layout.setSpacing(4)
        
        # A-B Seek bar layout
        seekbar_row = QHBoxLayout()
        seekbar_row.setSpacing(8)
        
        self.current_time_lbl = QLabel("00:00", self.controls_panel)
        self.current_time_lbl.setStyleSheet("font-family: Consolas, monospace; font-size: 10px;")
        seekbar_row.addWidget(self.current_time_lbl)
        
        self.slider = ABLoopSlider(self.controls_panel)
        self.slider.setRange(0, 1000)
        self.slider.sliderMoved.connect(self.slider_moved)
        self.slider.sliderPressed.connect(self.slider_pressed)
        self.slider.sliderReleased.connect(self.slider_released)
        seekbar_row.addWidget(self.slider, 1)
        
        self.total_time_lbl = QLabel("00:00", self.controls_panel)
        self.total_time_lbl.setStyleSheet("font-family: Consolas, monospace; font-size: 10px;")
        seekbar_row.addWidget(self.total_time_lbl)
        
        controls_layout.addLayout(seekbar_row)
        
        # Buttons Row
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(12)
        
        # Left controls buttons
        # Left controls buttons
        self.prev_btn = QPushButton("⏮", self.controls_panel)
        self.prev_btn.setFixedSize(30, 26)
        self.prev_btn.clicked.connect(self.play_previous)
        self.prev_btn.setToolTip("Previous Video (Shift+N)")
        buttons_row.addWidget(self.prev_btn)
        
        self.play_btn = QPushButton("▶", self.controls_panel)
        self.play_btn.setObjectName("play_btn")
        self.play_btn.setFixedSize(36, 30)
        self.play_btn.clicked.connect(self.toggle_play)
        buttons_row.addWidget(self.play_btn)
        
        self.next_btn = QPushButton("⏭", self.controls_panel)
        self.next_btn.setFixedSize(30, 26)
        self.next_btn.clicked.connect(self.play_next)
        self.next_btn.setToolTip("Next Video (N)")
        buttons_row.addWidget(self.next_btn)
        
        # Shuffle & Repeat
        self.shuffle_btn = QPushButton("🔀", self.controls_panel)
        self.shuffle_btn.setObjectName("shuffle_btn")
        self.shuffle_btn.setProperty("active", False)
        self.shuffle_btn.setFixedSize(30, 26)
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        buttons_row.addWidget(self.shuffle_btn)
        
        self.repeat_btn = QPushButton("🔁", self.controls_panel)
        self.repeat_btn.setObjectName("repeat_btn")
        self.repeat_btn.setProperty("repeat_mode", "off")
        self.repeat_btn.setFixedSize(30, 26)
        self.repeat_btn.clicked.connect(self.toggle_repeat)
        buttons_row.addWidget(self.repeat_btn)
        
        buttons_row.addSpacing(10)
        
        # Volume
        self.mute_btn = QPushButton("🔊", self.controls_panel)
        self.mute_btn.setFixedSize(30, 26)
        self.mute_btn.clicked.connect(self.toggle_mute)
        buttons_row.addWidget(self.mute_btn)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal, self.controls_panel)
        self.volume_slider.setRange(0, 150) # Allow up to 150% volume boost
        self.volume_slider.setValue(80)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.valueChanged.connect(self.volume_changed)
        buttons_row.addWidget(self.volume_slider)
        
        buttons_row.addStretch()
        
        # A-B looper segment trigger
        self.ab_loop_btn = QPushButton("A-B Loop", self.controls_panel)
        self.ab_loop_btn.setFixedSize(80, 26)
        self.ab_loop_btn.clicked.connect(self.trigger_ab_loop)
        buttons_row.addWidget(self.ab_loop_btn)
        
        # Aspect Ratio Selector
        aspect_lbl = QLabel("Aspect:", self.controls_panel)
        aspect_lbl.setStyleSheet("font-size: 10px;")
        buttons_row.addWidget(aspect_lbl)
        self.aspect_combo = QComboBox(self.controls_panel)
        self.aspect_combo.addItems(["Default", "16:9 Wide", "4:3 Standard", "21:9 UltraWide"])
        self.aspect_combo.currentIndexChanged.connect(self.aspect_ratio_changed)
        buttons_row.addWidget(self.aspect_combo)
        
        # Speeds Selector
        speed_lbl = QLabel("Speed:", self.controls_panel)
        speed_lbl.setStyleSheet("font-size: 10px;")
        buttons_row.addWidget(speed_lbl)
        self.speed_combo = QComboBox(self.controls_panel)
        self.speed_combo.addItems(["0.5x", "0.75x", "1.0x (Normal)", "1.25x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentIndex(2)
        self.speed_combo.currentIndexChanged.connect(self.speed_changed)
        buttons_row.addWidget(self.speed_combo)
        
        controls_layout.addLayout(buttons_row)
        self.video_area_layout.addWidget(self.controls_panel)
        
        content_layout.addWidget(self.video_area, 1)
        
        # Sidebar Section (Right)
        self.sidebar = QFrame(content_widget)
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(330)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs widget
        self.tabs = QTabWidget(self.sidebar)
        
        # TAB 1: Playlist
        playlist_tab = QWidget()
        play_tab_layout = QVBoxLayout(playlist_tab)
        
        lbl_info = QLabel("Playlist Queue (Drag & Drop files or load folder)", playlist_tab)
        lbl_info.setStyleSheet("font-size: 10px; color: var(--text-sec);")
        play_tab_layout.addWidget(lbl_info)
        
        self.playlist_list = DragDropListWidget(playlist_tab)
        self.playlist_list.setIconSize(QSize(64, 36))
        self.playlist_list.file_dropped.connect(self.add_local_file)
        self.playlist_list.itemDoubleClicked.connect(self.playlist_item_clicked)
        self.playlist_list.order_changed.connect(self.playlist_order_changed)
        play_tab_layout.addWidget(self.playlist_list, 1)
        
        playlist_actions = QHBoxLayout()
        self.add_file_btn = QPushButton("📂 Browse Files", playlist_tab)
        self.add_file_btn.clicked.connect(self.open_file_dialog)
        playlist_actions.addWidget(self.add_file_btn)
        
        self.add_url_btn = QPushButton("🔗 Add Stream URL", playlist_tab)
        self.add_url_btn.clicked.connect(self.open_url_dialog)
        playlist_actions.addWidget(self.add_url_btn)
        
        self.clear_list_btn = QPushButton("🗑 Clear", playlist_tab)
        self.clear_list_btn.clicked.connect(self.clear_playlist)
        playlist_actions.addWidget(self.clear_list_btn)
        play_tab_layout.addLayout(playlist_actions)
        
        self.remux_btn = QPushButton("⚡ One-Click Remux to MP4/MKV", playlist_tab)
        self.remux_btn.setObjectName("remux_btn")
        self.remux_btn.clicked.connect(self.start_one_click_remux)
        play_tab_layout.addWidget(self.remux_btn)
        
        self.remux_status_lbl = QLabel("", playlist_tab)
        self.remux_status_lbl.setStyleSheet("font-size: 10px; color: #f59e0b; font-weight: bold;")
        self.remux_status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        play_tab_layout.addWidget(self.remux_status_lbl)
        
        self.tabs.addTab(playlist_tab, "Playlist")
        
        # TAB 2: Equalizer & FX
        eq_tab = QWidget()
        eq_scroll = QScrollArea(eq_tab)
        eq_scroll.setWidgetResizable(True)
        eq_scroll.setFrameShape(QFrame.Shape.NoFrame)
        eq_scroll_content = QWidget()
        eq_layout = QVBoxLayout(eq_scroll_content)
        eq_layout.setContentsMargins(10, 10, 10, 10)
        
        # 10 Bands sliders layout (Horizontal container)
        bands_group = QGroupBox("10-Band Graphic Equalizer")
        bands_layout = QHBoxLayout(bands_group)
        bands_layout.setSpacing(6)
        
        self.eq_sliders = []
        bands_frequencies = ["31Hz", "62Hz", "125Hz", "250Hz", "500Hz", "1kHz", "2kHz", "4kHz", "8kHz", "16kHz"]
        for i in range(10):
            band_box = QVBoxLayout()
            slider = QSlider(Qt.Orientation.Vertical)
            slider.setRange(-20, 20)
            slider.setValue(0)
            slider.setFixedHeight(100)
            slider.valueChanged.connect(lambda val, idx=i: self.equalizer_band_changed(idx, val))
            
            lbl = QLabel(bands_frequencies[i])
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-size: 7px; color: var(--text-sec);")
            
            band_box.addWidget(slider, 1)
            band_box.addWidget(lbl)
            bands_layout.addLayout(band_box)
            self.eq_sliders.append(slider)
        
        eq_layout.addWidget(bands_group)
        
        # Equalizer Presets
        preset_layout = QHBoxLayout()
        preset_lbl = QLabel("EQ Preset:")
        preset_layout.addWidget(preset_lbl)
        self.eq_presets_combo = QComboBox()
        self.eq_presets_combo.addItems(["Flat", "Bass Boost", "Vocal Booster", "Classical", "Pop"])
        self.eq_presets_combo.currentIndexChanged.connect(self.apply_eq_preset)
        preset_layout.addWidget(self.eq_presets_combo)
        eq_layout.addLayout(preset_layout)
        
        # Audio Enhancements
        fx_group = QGroupBox("Audio FX Enhancements")
        fx_layout = QVBoxLayout(fx_group)
        
        self.normalizer_chk = QCheckBox("Auto Volume Normalizer (AGC)")
        self.normalizer_chk.setChecked(self.normalizer)
        self.normalizer_chk.stateChanged.connect(self.normalizer_changed)
        fx_layout.addWidget(self.normalizer_chk)
        
        self.night_mode_chk = QCheckBox("Movie Night Mode (Dialogue Booster)")
        self.night_mode_chk.setChecked(self.night_mode)
        self.night_mode_chk.stateChanged.connect(self.night_mode_changed)
        fx_layout.addWidget(self.night_mode_chk)
        
        # Pre-amp booster
        preamp_row = QHBoxLayout()
        preamp_row.addWidget(QLabel("Pre-amp Volume Boost:"))
        self.preamp_val_lbl = QLabel("0 dB")
        preamp_row.addWidget(self.preamp_val_lbl, 0, Qt.AlignmentFlag.AlignRight)
        fx_layout.addLayout(preamp_row)
        
        self.preamp_slider = QSlider(Qt.Orientation.Horizontal)
        self.preamp_slider.setRange(-20, 20)
        self.preamp_slider.setValue(0)
        self.preamp_slider.valueChanged.connect(self.preamp_changed)
        fx_layout.addWidget(self.preamp_slider)
        
        # Audio Delay Offset Slider
        delay_row = QHBoxLayout()
        delay_row.addWidget(QLabel("Audio Sync Delay:"))
        self.delay_val_lbl = QLabel("0 ms")
        delay_row.addWidget(self.delay_val_lbl, 0, Qt.AlignmentFlag.AlignRight)
        fx_layout.addLayout(delay_row)
        
        self.delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.delay_slider.setRange(-2000, 2000) # -2.0s to +2.0s
        self.delay_slider.setValue(0)
        self.delay_slider.valueChanged.connect(self.audio_delay_changed)
        fx_layout.addWidget(self.delay_slider)
        
        eq_layout.addWidget(fx_group)
        
        reset_eq_btn = QPushButton("Reset Audio Panel")
        reset_eq_btn.clicked.connect(self.reset_audio_panel)
        eq_layout.addWidget(reset_eq_btn)
        
        eq_scroll.setWidget(eq_scroll_content)
        eq_tab_layout = QVBoxLayout(eq_tab)
        eq_tab_layout.addWidget(eq_scroll)
        self.tabs.addTab(eq_tab, "EQ & FX")
        
        # TAB 3: Style Adjuster & Transformations
        style_tab = QWidget()
        style_scroll = QScrollArea(style_tab)
        style_scroll.setWidgetResizable(True)
        style_scroll.setFrameShape(QFrame.Shape.NoFrame)
        style_scroll_content = QWidget()
        style_layout = QVBoxLayout(style_scroll_content)
        
        # Theme/Colors Customization group
        theme_group = QGroupBox("App Themes & Custom Accent")
        theme_grid = QGridLayout(theme_group)
        
        theme_grid.addWidget(QLabel("Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Midnight Obsidian", "Cyberpunk Neon", "Glassmorphism Frost", "Classic Light"])
        # Map current theme to select index
        theme_indices = {"obsidian": 0, "cyberpunk": 1, "frost": 2, "light": 3}
        self.theme_combo.setCurrentIndex(theme_indices.get(self.theme, 0))
        self.theme_combo.currentIndexChanged.connect(self.theme_changed)
        theme_grid.addWidget(self.theme_combo, 0, 1)
        
        theme_grid.addWidget(QLabel("Accent Color:"), 1, 0)
        accent_btn_box = QHBoxLayout()
        self.accent_buttons = {}
        for name, color in ACCENT_COLORS.items():
            btn = QPushButton()
            btn.setFixedSize(22, 22)
            btn.clicked.connect(lambda checked=False, n=name: self.accent_changed(n))
            accent_btn_box.addWidget(btn)
            self.accent_buttons[name] = btn
        theme_grid.addLayout(accent_btn_box, 1, 1)
        
        theme_grid.addWidget(QLabel("Control Panel Style:"), 2, 0)
        self.control_style_combo = QComboBox()
        self.control_style_combo.addItems([
            "Transparent (Clear Glass)", 
            "Semi-Transparent (Blur Glass)", 
            "Frosted Acrylic (Translucent)", 
            "Solid Dark/Theme-Matching"
        ])
        controls_theme_indices = {"transparent": 0, "semi_transparent": 1, "frosted_acrylic": 2, "solid": 3}
        self.control_style_combo.setCurrentIndex(controls_theme_indices.get(self.controls_theme, 1))
        self.control_style_combo.currentIndexChanged.connect(self.controls_theme_changed)
        theme_grid.addWidget(self.control_style_combo, 2, 1)
        
        style_layout.addWidget(theme_group)
        
        # Video Transformation / Zoom & Pan Group
        transform_group = QGroupBox("Video Position & Transformations")
        trans_layout = QVBoxLayout(transform_group)
        
        # Zoom Level
        zoom_row = QHBoxLayout()
        zoom_row.addWidget(QLabel("Zoom Level:"))
        self.zoom_val_lbl = QLabel("1.0x")
        zoom_row.addWidget(self.zoom_val_lbl, 0, Qt.AlignmentFlag.AlignRight)
        trans_layout.addLayout(zoom_row)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 40) # 1.0x to 4.0x
        self.zoom_slider.setValue(10)
        self.zoom_slider.valueChanged.connect(self.zoom_changed)
        trans_layout.addWidget(self.zoom_slider)
        
        # Pan X
        pan_x_row = QHBoxLayout()
        pan_x_row.addWidget(QLabel("Offset X (Pan):"))
        self.pan_x_val_lbl = QLabel("0 px")
        pan_x_row.addWidget(self.pan_x_val_lbl, 0, Qt.AlignmentFlag.AlignRight)
        trans_layout.addLayout(pan_x_row)
        
        self.pan_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.pan_x_slider.setRange(-300, 300)
        self.pan_x_slider.setValue(0)
        self.pan_x_slider.valueChanged.connect(self.pan_x_changed)
        trans_layout.addWidget(self.pan_x_slider)
        
        # Pan Y
        pan_y_row = QHBoxLayout()
        pan_y_row.addWidget(QLabel("Offset Y (Pan):"))
        self.pan_y_val_lbl = QLabel("0 px")
        pan_y_row.addWidget(self.pan_y_val_lbl, 0, Qt.AlignmentFlag.AlignRight)
        trans_layout.addLayout(pan_y_row)
        
        self.pan_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.pan_y_slider.setRange(-300, 300)
        self.pan_y_slider.setValue(0)
        self.pan_y_slider.valueChanged.connect(self.pan_y_changed)
        trans_layout.addWidget(self.pan_y_slider)
        
        # Rotation & Flipping row
        extra_row = QHBoxLayout()
        extra_row.addWidget(QLabel("Rotation angle:"))
        self.rot_combo = QComboBox()
        self.rot_combo.addItems(["0°", "90°", "180°", "270°"])
        self.rot_combo.currentIndexChanged.connect(self.rotation_changed)
        extra_row.addWidget(self.rot_combo)
        
        self.mirror_btn = QPushButton("Flip Horizontal")
        self.mirror_btn.setObjectName("mirror_btn")
        self.mirror_btn.setCheckable(True)
        self.mirror_btn.clicked.connect(self.mirror_changed)
        extra_row.addWidget(self.mirror_btn)
        trans_layout.addLayout(extra_row)
        
        style_layout.addWidget(transform_group)
        
        reset_trans_btn = QPushButton("Reset Video Geometry")
        reset_trans_btn.clicked.connect(self.reset_video_geometry)
        style_layout.addWidget(reset_trans_btn)
        
        # Video Adjustment Filters Group
        filters_group = QGroupBox("Video Adjustment Filters")
        filters_layout = QVBoxLayout(filters_group)
        
        # Brightness Slider
        brightness_row = QHBoxLayout()
        brightness_row.addWidget(QLabel("Brightness:"))
        self.brightness_val_lbl = QLabel("1.0")
        brightness_row.addWidget(self.brightness_val_lbl, 0, Qt.AlignmentFlag.AlignRight)
        filters_layout.addLayout(brightness_row)
        
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 20) # 0.0 to 2.0
        self.brightness_slider.setValue(10) # 1.0 default
        self.brightness_slider.valueChanged.connect(self.brightness_changed)
        filters_layout.addWidget(self.brightness_slider)
        
        # Contrast Slider
        contrast_row = QHBoxLayout()
        contrast_row.addWidget(QLabel("Contrast:"))
        self.contrast_val_lbl = QLabel("1.0")
        contrast_row.addWidget(self.contrast_val_lbl, 0, Qt.AlignmentFlag.AlignRight)
        filters_layout.addLayout(contrast_row)
        
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(0, 20) # 0.0 to 2.0
        self.contrast_slider.setValue(10) # 1.0 default
        self.contrast_slider.valueChanged.connect(self.contrast_changed)
        filters_layout.addWidget(self.contrast_slider)
        
        # Saturation Slider
        saturation_row = QHBoxLayout()
        saturation_row.addWidget(QLabel("Saturation:"))
        self.saturation_val_lbl = QLabel("1.0")
        saturation_row.addWidget(self.saturation_val_lbl, 0, Qt.AlignmentFlag.AlignRight)
        filters_layout.addLayout(saturation_row)
        
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(0, 30) # 0.0 to 3.0
        self.saturation_slider.setValue(10) # 1.0 default
        self.saturation_slider.valueChanged.connect(self.saturation_changed)
        filters_layout.addWidget(self.saturation_slider)
        
        # Hue Slider
        hue_row = QHBoxLayout()
        hue_row.addWidget(QLabel("Hue:"))
        self.hue_val_lbl = QLabel("0°")
        hue_row.addWidget(self.hue_val_lbl, 0, Qt.AlignmentFlag.AlignRight)
        filters_layout.addLayout(hue_row)
        
        self.hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.hue_slider.setRange(0, 360) # 0 to 360 degrees
        self.hue_slider.setValue(0) # 0 default
        self.hue_slider.valueChanged.connect(self.hue_changed)
        filters_layout.addWidget(self.hue_slider)
        
        style_layout.addWidget(filters_group)
        
        reset_filters_btn = QPushButton("Reset Video Filters")
        reset_filters_btn.clicked.connect(self.reset_video_filters)
        style_layout.addWidget(reset_filters_btn)
        
        style_scroll.setWidget(style_scroll_content)
        style_tab_layout = QVBoxLayout(style_tab)
        style_tab_layout.addWidget(style_scroll)
        self.tabs.addTab(style_tab, "Style")
        
        # TAB 4: Shortcuts Rebinding GUI
        shortcuts_tab = QWidget()
        shortcuts_scroll = QScrollArea(shortcuts_tab)
        shortcuts_scroll.setWidgetResizable(True)
        shortcuts_scroll.setFrameShape(QFrame.Shape.NoFrame)
        shortcuts_scroll_content = QWidget()
        self.shortcuts_layout = QVBoxLayout(shortcuts_scroll_content)
        self.shortcuts_layout.setContentsMargins(10, 10, 10, 10)
        self.shortcuts_layout.setSpacing(8)
        
        shortcuts_scroll.setWidget(shortcuts_scroll_content)
        shortcuts_tab_layout = QVBoxLayout(shortcuts_tab)
        shortcuts_tab_layout.addWidget(shortcuts_scroll)
        self.tabs.addTab(shortcuts_tab, "Shortcuts")
        
        # TAB 5: Subtitles
        subtitles_tab = QWidget()
        sub_layout = QVBoxLayout(subtitles_tab)
        sub_layout.setContentsMargins(10, 10, 10, 10)
        sub_layout.setSpacing(10)
        
        # External Subtitle Group
        ext_sub_group = QGroupBox("External Subtitles")
        ext_sub_layout = QVBoxLayout(ext_sub_group)
        self.load_sub_btn = QPushButton("📂 Load Subtitle File (.srt, .vtt, .ass)")
        self.load_sub_btn.clicked.connect(self.load_external_subtitle)
        ext_sub_layout.addWidget(self.load_sub_btn)
        
        self.sub_file_lbl = QLabel("No subtitle file loaded")
        self.sub_file_lbl.setStyleSheet("font-size: 10px; color: var(--text-sec);")
        ext_sub_layout.addWidget(self.sub_file_lbl)
        sub_layout.addWidget(ext_sub_group)
        
        # Subtitle Sync Group
        sync_group = QGroupBox("Subtitle Sync (Delay)")
        sync_layout = QVBoxLayout(sync_group)
        
        sync_btn_layout = QHBoxLayout()
        self.sub_delay_minus_btn = QPushButton("-0.5s")
        self.sub_delay_minus_btn.clicked.connect(lambda: self.adjust_sub_delay(-0.5))
        sync_btn_layout.addWidget(self.sub_delay_minus_btn)
        
        self.sub_delay_plus_btn = QPushButton("+0.5s")
        self.sub_delay_plus_btn.clicked.connect(lambda: self.adjust_sub_delay(0.5))
        sync_btn_layout.addWidget(self.sub_delay_plus_btn)
        
        self.sub_delay_reset_btn = QPushButton("Reset Delay")
        self.sub_delay_reset_btn.clicked.connect(self.reset_sub_delay)
        sync_btn_layout.addWidget(self.sub_delay_reset_btn)
        sync_layout.addLayout(sync_btn_layout)
        
        self.sub_delay_lbl = QLabel("Delay Offset: 0.0s")
        self.sub_delay_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub_delay_lbl.setStyleSheet("font-weight: bold;")
        sync_layout.addWidget(self.sub_delay_lbl)
        sub_layout.addWidget(sync_group)
        
        # Subtitle Tracks Group
        tracks_group = QGroupBox("Embedded Subtitle Tracks")
        tracks_layout = QVBoxLayout(tracks_group)
        self.sub_track_combo = QComboBox()
        self.sub_track_combo.currentIndexChanged.connect(self.sub_track_changed)
        tracks_layout.addWidget(self.sub_track_combo)
        
        self.refresh_sub_tracks_btn = QPushButton("🔄 Refresh Subtitle Tracks")
        self.refresh_sub_tracks_btn.clicked.connect(self.refresh_subtitle_tracks)
        tracks_layout.addWidget(self.refresh_sub_tracks_btn)
        sub_layout.addWidget(tracks_group)
        
        sub_layout.addStretch()
        self.tabs.addTab(subtitles_tab, "Subtitles")
        
        # TAB 6: Bookmarks
        bookmarks_tab = QWidget()
        bookmarks_layout = QVBoxLayout(bookmarks_tab)
        bookmarks_layout.setContentsMargins(10, 10, 10, 10)
        bookmarks_layout.setSpacing(10)
        
        bookmark_add_layout = QHBoxLayout()
        self.bookmark_input = QLineEdit()
        self.bookmark_input.setPlaceholderText("Enter bookmark note...")
        bookmark_add_layout.addWidget(self.bookmark_input, 1)
        
        self.add_bookmark_btn = QPushButton("+ Add")
        self.add_bookmark_btn.clicked.connect(self.add_bookmark)
        bookmark_add_layout.addWidget(self.add_bookmark_btn)
        bookmark_add_layout.setSpacing(6)
        bookmarks_layout.addLayout(bookmark_add_layout)
        
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.itemDoubleClicked.connect(self.bookmark_clicked)
        bookmarks_layout.addWidget(self.bookmarks_list, 1)
        
        self.delete_bookmark_btn = QPushButton("🗑 Delete Selected")
        self.delete_bookmark_btn.clicked.connect(self.delete_bookmark)
        bookmarks_layout.addWidget(self.delete_bookmark_btn)
        
        self.tabs.addTab(bookmarks_tab, "Bookmarks")
        
        # TAB 7: Library
        library_tab = QWidget()
        lib_layout = QVBoxLayout(library_tab)
        lib_layout.setContentsMargins(10, 10, 10, 10)
        lib_layout.setSpacing(10)
        
        lib_actions = QHBoxLayout()
        self.scan_folder_btn = QPushButton("📁 Scan Folder")
        self.scan_folder_btn.clicked.connect(self.scan_folder_dialog)
        lib_actions.addWidget(self.scan_folder_btn)
        
        self.rescan_lib_btn = QPushButton("🔄 Rescan")
        self.rescan_lib_btn.clicked.connect(self.rescan_library)
        lib_actions.addWidget(self.rescan_lib_btn)
        lib_layout.addLayout(lib_actions)
        
        self.lib_path_lbl = QLabel("No active folder scanned")
        self.lib_path_lbl.setStyleSheet("font-size: 10px; color: var(--text-sec);")
        self.lib_path_lbl.setWordWrap(True)
        lib_layout.addWidget(self.lib_path_lbl)
        
        self.library_list = LibraryListWidget()
        self.library_list.setIconSize(QSize(64, 36))
        self.library_list.itemDoubleClicked.connect(self.library_item_clicked)
        lib_layout.addWidget(self.library_list, 1)
        
        self.tabs.addTab(library_tab, "Library")
        
        # TAB 8: About & Support
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setContentsMargins(12, 12, 12, 12)
        about_layout.setSpacing(12)

        about_group = QGroupBox("About BingeBox")
        about_g_layout = QVBoxLayout(about_group)
        
        app_title_lbl = QLabel("🎬 BingeBox Media Player v1.0.0")
        app_title_lbl.setStyleSheet("font-weight: bold; font-size: 13px;")
        about_g_layout.addWidget(app_title_lbl)
        
        app_desc_lbl = QLabel("100% Standalone, 100% Offline & Private Media Player.\nPowered by libmpv, PySide6, and FFmpeg.\nDeveloped with ❤️ by CAPTAIN NEMO.")
        app_desc_lbl.setStyleSheet("color: var(--text-sec); font-size: 11px;")
        app_desc_lbl.setWordWrap(True)
        about_g_layout.addWidget(app_desc_lbl)
        about_layout.addWidget(about_group)

        support_group = QGroupBox("Support Development")
        support_g_layout = QVBoxLayout(support_group)
        
        support_desc_lbl = QLabel("If you enjoy using BingeBox, consider supporting the developer to fund ongoing features and updates!")
        support_desc_lbl.setStyleSheet("font-size: 11px;")
        support_desc_lbl.setWordWrap(True)
        support_g_layout.addWidget(support_desc_lbl)

        self.support_btn = QPushButton("☕ Buy Me a Coffee")
        self.support_btn.setStyleSheet("background-color: #FFDD00; color: #000000; font-weight: bold; border-radius: 6px; padding: 8px;")
        self.support_btn.clicked.connect(self.open_buy_me_a_coffee)
        support_g_layout.addWidget(self.support_btn)
        
        about_layout.addWidget(support_group)
        about_layout.addStretch()
        
        self.tabs.addTab(about_tab, "About")
        
        sidebar_layout.addWidget(self.tabs)
        content_layout.addWidget(self.sidebar)
        
        self.main_layout.addWidget(content_widget, 1)
        
        # Layout styling configs
        self.resize(1180, 680)

    # ==========================================================================
    # WINDOW CONTROLS AND GEOMETRY TRANSLATIONS
    # ==========================================================================

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def titlebar_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def titlebar_move(self, event):
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = event.globalPosition().toPoint()

    def titlebar_double_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()

    def video_container_resized(self, event):
        self.update_video_geometry()

    def update_video_geometry(self):
        # Apply Zoom & Pan absolute geometry positioning
        cw = self.video_container.width()
        ch = self.video_container.height()
        
        if cw <= 0 or ch <= 0:
            return
            
        new_w = int(cw * self.zoom_level)
        new_h = int(ch * self.zoom_level)
        
        pos_x = int((cw - new_w) / 2) + self.pan_x
        pos_y = int((ch - new_h) / 2) + self.pan_y
        
        self.video_frame.setGeometry(pos_x, pos_y, new_w, new_h)

    # ==========================================================================
    # THEME SWITCHER
    # ==========================================================================

    def apply_theme(self):
        self.setStyleSheet(get_theme_qss(self.theme, self.accent))
        self.apply_controls_theme()
        
        # Style color picker circles in-place based on theme & selected accent
        if hasattr(self, "accent_buttons") and self.accent_buttons:
            for btn_name, btn in self.accent_buttons.items():
                color = ACCENT_COLORS[btn_name]
                if self.accent == btn_name:
                    border_color = "#0f172a" if self.theme in ("frost", "light") else "#ffffff"
                else:
                    border_color = "transparent"
                btn.setStyleSheet(f"background-color: {color}; border-radius: 11px; border: 2px solid {border_color};")
                
        self.save_settings()

    def apply_controls_theme(self):
        if not hasattr(self, "controls_panel"):
            return
            
        style_opt = getattr(self, "controls_theme", "semi_transparent")
        is_light = self.theme in ("frost", "light")
        border = "rgba(0, 0, 0, 0.08)" if is_light else "rgba(255, 255, 255, 0.05)"
        
        if style_opt == "transparent":
            bg = "rgba(0, 0, 0, 0)"
        elif style_opt == "semi_transparent":
            bg = "rgba(241, 245, 249, 0.45)" if is_light else "rgba(6, 9, 19, 0.5)"
        elif style_opt == "frosted_acrylic":
            bg = "rgba(255, 255, 255, 0.75)" if is_light else "rgba(13, 17, 28, 0.75)"
        else: # solid
            bg = "#ffffff" if self.theme == "light" else "#f1f5f9" if self.theme == "frost" else "#120121" if self.theme == "cyberpunk" else "#0d111c"
            
        self.controls_panel.setStyleSheet(f"background-color: {bg}; border-top: 1px solid {border};")

    def theme_changed(self, index):
        themes = ["obsidian", "cyberpunk", "frost", "light"]
        if 0 <= index < len(themes):
            self.theme = themes[index]
            self.apply_theme()

    def accent_changed(self, name):
        if name in ACCENT_COLORS:
            self.accent = name
            self.apply_theme()
            self.update_shortcuts_ui()

    def controls_theme_changed(self, index):
        opts = ["transparent", "semi_transparent", "frosted_acrylic", "solid"]
        if 0 <= index < len(opts):
            self.controls_theme = opts[index]
            self.apply_controls_theme()
            self.save_settings()

    # ==========================================================================
    # PLAYLIST MANAGEMENT
    # ==========================================================================

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Open Video Files", "",
            "Video files (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.ts *.mp3 *.wav *.flac);;All files (*.*)"
        )
        for f in files:
            self.add_local_file(f)

    def add_local_file(self, path):
        if path not in self.playlist:
            self.playlist.append(path)
            self.save_settings()
            
            filename = os.path.basename(path)
            item = QListWidgetItem(filename)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.playlist_list.addItem(item)
            self.request_thumbnail(path, item)
            
            if len(self.playlist) == 1:
                self.load_video(0)

    def populate_playlist_list(self):
        self.playlist_list.clear()
        for path in self.playlist:
            filename = os.path.basename(path)
            item = QListWidgetItem(filename)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.playlist_list.addItem(item)
            self.request_thumbnail(path, item)
            
        if 0 <= self.current_index < self.playlist_list.count():
            self.playlist_list.setCurrentRow(self.current_index)

    def playlist_order_changed(self):
        if not self.playlist:
            return
        # Store currently playing video path to keep current index pointer correct
        current_playing_path = self.playlist[self.current_index] if 0 <= self.current_index < len(self.playlist) else None
        
        new_playlist = []
        for i in range(self.playlist_list.count()):
            item = self.playlist_list.item(i)
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                new_playlist.append(path)
                
        self.playlist = new_playlist
        self.save_settings()
        
        # Sync index
        if current_playing_path and current_playing_path in self.playlist:
            self.current_index = self.playlist.index(current_playing_path)
            self.playlist_list.setCurrentRow(self.current_index)
        else:
            self.current_index = -1

    def start_one_click_remux(self):
        if self.current_index < 0 or self.current_index >= len(self.playlist):
            self.remux_status_lbl.setText("❌ No active video to remux!")
            QTimer.singleShot(3000, lambda: self.remux_status_lbl.setText(""))
            return
            
        input_path = self.playlist[self.current_index]
        if not os.path.exists(input_path):
            self.remux_status_lbl.setText("❌ Video file not found!")
            QTimer.singleShot(3000, lambda: self.remux_status_lbl.setText(""))
            return
            
        input_dir = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        input_ext = os.path.splitext(input_path)[1].lower()
        
        if input_ext == ".mp4":
            output_ext = ".mkv"
            mux_format = "mkv"
        else:
            output_ext = ".mp4"
            mux_format = "mp4"
            
        output_name = f"{base_name}_remuxed{output_ext}"
        output_path = os.path.join(input_dir, output_name)
        
        # Avoid overwriting existing files
        counter = 1
        while os.path.exists(output_path):
            output_name = f"{base_name}_remuxed_{counter}{output_ext}"
            output_path = os.path.join(input_dir, output_name)
            counter += 1
            
        self.remux_status_lbl.setText(f"⚡ Remuxing to {os.path.basename(output_path)}...")
        self.remux_btn.setEnabled(False)
        
        # Run QProcess in background
        self.remux_process = QProcess(self)
        self.remux_process.finished.connect(lambda exit_code, exit_status, op=output_path: self.remux_finished(exit_code, exit_status, op))
        
        # Remux instantaneously using bundled FFmpeg engine (lossless stream copy)
        args = ["-y", "-i", input_path, "-c", "copy", output_path]
        self.remux_process.start(FFMPEG_BIN, args)

    def remux_finished(self, exit_code, exit_status, output_path):
        self.remux_btn.setEnabled(True)
        if exit_code == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            filename = os.path.basename(output_path)
            self.remux_status_lbl.setText(f"✅ Saved as {filename}!")
            # Add file to playlist and select it
            self.add_local_file(output_path)
        else:
            self.remux_status_lbl.setText("❌ Remux failed or was aborted!")
            
        QTimer.singleShot(5000, lambda: self.remux_status_lbl.setText(""))

    def clear_playlist(self):
        if self.mpv_player:
            self.mpv_player.stop()
        self.playlist = []
        self.playlist_list.clear()
        self.current_index = -1
        self.save_settings()
        self.update_playback_progress()

    def playlist_item_clicked(self, item):
        idx = self.playlist_list.row(item)
        self.load_video(idx)
        self.play_video()

    def load_video(self, index):
        if index < 0 or index >= len(self.playlist):
            return
            
        self.current_index = index
        self.playlist_list.setCurrentRow(index)
        
        path = self.playlist[index]
        
        # MPV audio filters applied via apply_equalizer_settings
            
        # Transform adjustments (Mirror & Rotation)
        if self.mirror_enabled or self.rotation_angle != 0:
            media_opts.append(":video-filter=transform")
            if self.mirror_enabled:
                media_opts.append(":transform-type=hflip")
            elif self.rotation_angle == 90:
                media_opts.append(":transform-type=90")
            elif self.rotation_angle == 180:
                media_opts.append(":transform-type=180")
            elif self.rotation_angle == 270:
                media_opts.append(":transform-type=270")
                
        # Load and play video via mpv engine
        if self.mpv_player:
            try:
                self.mpv_player.play(path)
                self.mpv_player.pause = False
                self.mpv_player.mute = False
                vol_val = self.volume_slider.value() if hasattr(self, 'volume_slider') else 80
                self.mpv_player.volume = vol_val
                self.mpv_player.aid = "auto"
            except Exception as e:
                print("Failed to play video via mpv:", e)
        
        # Reset local GUI transformations
        self.reset_video_geometry()
        
        # Reset A-B Loop boundaries
        self.ab_start = None
        self.ab_end = None
        self.ab_active = False
        self.ab_loop_btn.setObjectName("")
        self.ab_loop_btn.style().unpolish(self.ab_loop_btn)
        self.ab_loop_btn.style().polish(self.ab_loop_btn)
        self.ab_loop_btn.update()
        self.slider.set_ab_loop(None, None, False)
        
        # Load equalizer
        self.apply_equalizer_settings()
        
        # Apply current video filters adjustments
        if hasattr(self, "brightness_slider"):
            self.update_vlc_adjust_filter()
        
        # Reset subtitle delay display & external file label
        if hasattr(self, "sub_delay_lbl"):
            self.sub_delay_lbl.setText("Delay Offset: 0.0s")
            self.sub_file_lbl.setText("No subtitle file loaded")
        
        # Trigger embedded tracks refresh after media starts loading
        if hasattr(self, "refresh_subtitle_tracks"):
            QTimer.singleShot(1000, self.refresh_subtitle_tracks)
        
        # Update bookmarks for new video
        if hasattr(self, "update_bookmarks_ui"):
            self.update_bookmarks_ui()
        
        # Trigger layout refresh sizes
        self.update_playback_progress()

    def play_video(self):
        if self.mpv_player:
            self.mpv_player.pause = False
        self.play_btn.setText("⏸")
        self.timer.start()
        QTimer.singleShot(1500, self.capture_mpv_snapshot)

    def capture_mpv_snapshot(self, retry_count=0):
        if not self.playlist or self.current_index < 0 or self.current_index >= len(self.playlist):
            return
            
        video_path = self.playlist[self.current_index]
        worker = ThumbnailWorker(video_path)
        def on_finished(v_path, t_path):
            self.update_ui_thumbnails(v_path, t_path)
        worker.signals.finished.connect(on_finished)
        self.thread_pool.start(worker)

    def update_ui_thumbnails(self, video_path, thumb_path):
        # Update icons for all matching items in playlist
        for i in range(self.playlist_list.count()):
            li = self.playlist_list.item(i)
            if li.data(Qt.ItemDataRole.UserRole) == video_path:
                li.setIcon(QIcon(thumb_path))
        # and in library
        for i in range(self.library_list.count()):
            li = self.library_list.item(i)
            if li.data(Qt.ItemDataRole.UserRole) == video_path:
                li.setIcon(QIcon(thumb_path))

    def pause_video(self):
        if self.mpv_player:
            self.mpv_player.pause = True
        self.play_btn.setText("▶")
        self.timer.stop()

    def toggle_play(self):
        if self.mpv_player and not self.mpv_player.pause:
            self.pause_video()
        else:
            self.play_video()

    def seek_backward(self):
        if self.mpv_player:
            curr = self.mpv_player.time_pos or 0
            self.mpv_player.time_pos = max(0, curr - 5.0)
            self.update_playback_progress()

    def seek_forward(self):
        if self.mpv_player:
            curr = self.mpv_player.time_pos or 0
            dur = self.mpv_player.duration or 0
            if dur > 0:
                self.mpv_player.time_pos = min(dur, curr + 5.0)
            self.update_playback_progress()

    def play_next(self, is_auto=False):
        if not self.playlist:
            return
            
        if is_auto and self.repeat_mode == "one":
            # Repeat the current video
            self.load_video(self.current_index)
            self.play_video()
            return
            
        if self.shuffle_enabled and len(self.playlist) > 1:
            import random
            # Select a random index that is not the current one
            next_idx = self.current_index
            while next_idx == self.current_index:
                next_idx = random.randint(0, len(self.playlist) - 1)
        else:
            next_idx = self.current_index + 1
            if next_idx >= len(self.playlist):
                if is_auto and self.repeat_mode == "off":
                    # Stop playback at the end of the playlist
                    if self.mpv_player:
                        self.mpv_player.stop()
                    self.play_btn.setText("▶")
                    self.timer.stop()
                    self.slider.setValue(0)
                    self.current_time_lbl.setText("00:00")
                    return
                else:
                    next_idx = 0
                    
        self.load_video(next_idx)
        self.play_video()

    def play_previous(self):
        if not self.playlist:
            return
            
        if self.shuffle_enabled and len(self.playlist) > 1:
            import random
            prev_idx = self.current_index
            while prev_idx == self.current_index:
                prev_idx = random.randint(0, len(self.playlist) - 1)
        else:
            prev_idx = self.current_index - 1
            if prev_idx < 0:
                prev_idx = len(self.playlist) - 1
                
        self.load_video(prev_idx)
        self.play_video()

    def toggle_shuffle(self):
        self.shuffle_enabled = not self.shuffle_enabled
        self.shuffle_btn.setProperty("active", self.shuffle_enabled)
        self.shuffle_btn.style().unpolish(self.shuffle_btn)
        self.shuffle_btn.style().polish(self.shuffle_btn)
        self.shuffle_btn.update()

    def toggle_repeat(self):
        if self.repeat_mode == "off":
            self.repeat_mode = "all"
            self.repeat_btn.setText("🔁")
        elif self.repeat_mode == "all":
            self.repeat_mode = "one"
            self.repeat_btn.setText("🔂")
        else:
            self.repeat_mode = "off"
            self.repeat_btn.setText("🔁")
            
        self.repeat_btn.setProperty("repeat_mode", self.repeat_mode)
        self.repeat_btn.style().unpolish(self.repeat_btn)
        self.repeat_btn.style().polish(self.repeat_btn)
        self.repeat_btn.update()

    # ==========================================================================
    # VOLUME & MEDIA AUDIO CALLBACKS
    # ==========================================================================

    def toggle_mute(self):
        if self.mpv_player:
            is_muted = getattr(self.mpv_player, 'mute', False)
            self.mpv_player.mute = not is_muted
            self.mute_btn.setText("🔇" if not is_muted else "🔊")

    def volume_changed(self, value):
        if self.mpv_player:
            self.mpv_player.volume = value
            if value == 0:
                self.mute_btn.setText("🔇")
            elif value < 50:
                self.mute_btn.setText("🔈")
            elif value < 100:
                self.mute_btn.setText("🔉")
            else:
                self.mute_btn.setText("🔊")
        else:
            self.mute_btn.setText("🔊")

    def preamp_changed(self, value):
        self.preamp = float(value)
        self.preamp_val_lbl.setText(f"{value} dB")
        self.apply_equalizer_settings()

    def audio_delay_changed(self, value):
        self.audio_delay = float(value) / 1000.0 # convert ms to seconds
        self.delay_val_lbl.setText(f"{value} ms")
        if self.mpv_player:
            self.mpv_player.audio_delay = self.audio_delay

    def normalizer_changed(self, state_val):
        self.normalizer = (state_val == Qt.CheckState.Checked.value)
        self.save_settings()
        if self.mpv_player:
            pos_sec = self.mpv_player.time_pos or 0
            self.load_video(self.current_index)
            self.mpv_player.time_pos = pos_sec
            self.play_video()

    def night_mode_changed(self, state_val):
        self.night_mode = (state_val == Qt.CheckState.Checked.value)
        self.save_settings()
        if self.mpv_player:
            pos_sec = self.mpv_player.time_pos or 0
            self.load_video(self.current_index)
            self.mpv_player.time_pos = pos_sec
            self.play_video()

    # ==========================================================================
    # NATIVE 10-BAND EQUALIZER HANDLERS
    # ==========================================================================

    def apply_equalizer_settings(self):
        if self.mpv_player:
            try:
                if all(b == 0 for b in self.eq_bands):
                    self.mpv_player['af'] = ""
                else:
                    g0 = self.eq_bands[0] if len(self.eq_bands) > 0 else 0
                    g1 = self.eq_bands[1] if len(self.eq_bands) > 1 else 0
                    g2 = self.eq_bands[2] if len(self.eq_bands) > 2 else 0
                    g3 = self.eq_bands[3] if len(self.eq_bands) > 3 else 0
                    g4 = self.eq_bands[4] if len(self.eq_bands) > 4 else 0
                    self.mpv_player['af'] = f"equalizer=g0={g0}:g1={g1}:g2={g2}:g3={g3}:g4={g4}"
            except Exception as e:
                print("Equalizer update note:", e)

    def equalizer_band_changed(self, index, value):
        self.eq_bands[index] = float(value)
        self.apply_equalizer_settings()

    def apply_eq_preset(self, index):
        presets = {
            0: [0.0] * 10,  # Flat
            1: [8.0, 6.0, 4.0, 0.0, 0.0, -2.0, -4.0, -4.0, -6.0, -6.0], # Bass Boost
            2: [-4.0, -2.0, 0.0, 2.0, 4.0, 5.0, 5.0, 4.0, 2.0, 0.0],    # Vocal Booster
            3: [5.0, 4.0, 3.0, 2.0, -1.0, -1.0, 0.0, 2.0, 4.0, 5.0],    # Classical
            4: [-2.0, 0.0, 2.0, 4.0, 5.0, 3.0, 1.0, 0.0, -1.0, -2.0]    # Pop
        }
        
        gains = presets.get(index, [0.0] * 10)
        for i in range(10):
            self.eq_sliders[i].setValue(int(gains[i]))
            self.eq_bands[i] = gains[i]
        self.apply_equalizer_settings()

    def reset_audio_panel(self):
        # Reset equalizer to flat
        self.eq_presets_combo.setCurrentIndex(0)
        self.apply_eq_preset(0)
        
        # Reset sliders
        self.preamp_slider.setValue(0)
        self.delay_slider.setValue(0)
        self.normalizer_chk.setChecked(False)
        self.night_mode_chk.setChecked(False)

    # ==========================================================================
    # VIDEO GEOMETRY TRANSFORMATIONS HANDLERS
    # ==========================================================================

    def zoom_changed(self, value):
        self.zoom_level = float(value) / 10.0
        self.zoom_val_lbl.setText(f"{self.zoom_level:.1f}x")
        self.update_video_geometry()

    def pan_x_changed(self, value):
        self.pan_x = value
        self.pan_x_val_lbl.setText(f"{value} px")
        self.update_video_geometry()

    def pan_y_changed(self, value):
        self.pan_y = value
        self.pan_y_val_lbl.setText(f"{value} px")
        self.update_video_geometry()

    def rotation_changed(self, index):
        angles = [0, 90, 180, 270]
        if 0 <= index < len(angles):
            self.rotation_angle = angles[index]
            if self.mpv_player:
                self.mpv_player.video_rotate = self.rotation_angle

    def mirror_changed(self, checked):
        self.mirror_enabled = checked
        if self.mpv_player:
            self.mpv_player.vf = "hflip" if checked else ""

    def reset_video_geometry(self):
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.rotation_angle = 0
        self.mirror_enabled = False
        
        # Reset sliders
        self.zoom_slider.setValue(10)
        self.pan_x_slider.setValue(0)
        self.pan_y_slider.setValue(0)
        self.rot_combo.setCurrentIndex(0)
        self.mirror_btn.setChecked(False)
        
        self.update_video_geometry()

    def aspect_ratio_changed(self, index):
        ratios = ["-1", "16:9", "4:3", "21:9"]
        if 0 <= index < len(ratios) and self.mpv_player:
            self.mpv_player.video_aspect_override = ratios[index]

    def speed_changed(self, index):
        speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        if 0 <= index < len(speeds) and self.mpv_player:
            self.mpv_player.speed = speeds[index]

    # ==========================================================================
    # A-B LOOPER SEGMENT LOOP FUNCTIONS
    # ==========================================================================

    def trigger_ab_loop(self):
        if not self.mpv_player:
            return
        length = int((self.mpv_player.duration or 0) * 1000)
        if length <= 0:
            return
            
        curr_time = int((self.mpv_player.time_pos or 0) * 1000)
        
        if self.ab_start is None:
            self.ab_start = curr_time
            self.ab_loop_btn.setText("Set End [B]")
            self.ab_loop_btn.setObjectName("ab_btn_active")
            self.slider.set_ab_loop(self.ab_start, None, False)
        elif self.ab_end is None:
            self.ab_end = curr_time
            if self.ab_end < self.ab_start:
                self.ab_start, self.ab_end = self.ab_end, self.ab_start
            if self.ab_end - self.ab_start < 200:
                self.ab_end = self.ab_start + 200
            self.ab_active = True
            self.ab_loop_btn.setText("Clear Loop")
            self.mpv_player.time_pos = self.ab_start / 1000.0
            self.slider.set_ab_loop(self.ab_start, self.ab_end, True)
        else:
            self.ab_start = None
            self.ab_end = None
            self.ab_active = False
            self.ab_loop_btn.setText("A-B Loop")
            self.ab_loop_btn.setObjectName("")
            self.slider.set_ab_loop(None, None, False)
            
        self.ab_loop_btn.style().unpolish(self.ab_loop_btn)
        self.ab_loop_btn.style().polish(self.ab_loop_btn)
        self.ab_loop_btn.update()

    # ==========================================================================
    # TIMELINE SEEKBAR INTERACTIVITY
    # ==========================================================================

    def slider_moved(self, position):
        if self.mpv_player:
            self.mpv_player.time_pos = position / 1000.0

    def slider_pressed(self):
        self._slider_active = True

    def slider_released(self):
        self._slider_active = False

    def update_playback_progress(self):
        if not self.mpv_player:
            return
            
        if getattr(self.mpv_player, 'eof_reached', False) or getattr(self.mpv_player, 'idle_active', False):
            self.play_next(is_auto=True)
            return
            
        length = int((self.mpv_player.duration or 0) * 1000)
        time = int((self.mpv_player.time_pos or 0) * 1000)
        
        if length > 0:
            self.slider.setMaximum(length)
            if not getattr(self, "_slider_active", False):
                self.slider.setValue(time)
                
            cur_secs = int(time / 1000)
            tot_secs = int(length / 1000)
            
            cur_str = f"{cur_secs // 60:02d}:{cur_secs % 60:02d}"
            tot_str = f"{tot_secs // 60:02d}:{tot_secs % 60:02d}"
            
            self.current_time_lbl.setText(cur_str)
            self.total_time_lbl.setText(tot_str)
            
            if self.ab_active and self.ab_start is not None and self.ab_end is not None:
                if time >= self.ab_end or time < self.ab_start:
                    self.mpv_player.time_pos = self.ab_start / 1000.0
        else:
            self.slider.setMaximum(0)
            self.slider.setValue(0)
            self.current_time_lbl.setText("00:00")
            self.total_time_lbl.setText("00:00")

    # ==========================================================================
    # KEYBOARD SHORTCUTS AND INTERACTIVITY
    # ==========================================================================

    def update_shortcuts_ui(self):
        # Clear layout
        while self.shortcuts_layout.count():
            child = self.shortcuts_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_sublayout(child.layout())
                
        accent_hex = ACCENT_COLORS.get(self.accent, "#8b5cf6")
        
        # Populate each hotkey
        for action, data in self.hotkeys.items():
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            lbl = QLabel(data["label"])
            lbl.setStyleSheet("font-size: 11px; font-weight: bold;")
            
            btn = QPushButton()
            if self.rebinding_action == action:
                btn.setText("Press Key...")
                btn.setProperty("rebinding", True)
            else:
                btn.setText(data["key"])
                
            btn.setFixedWidth(120)
            btn.clicked.connect(lambda checked=False, act=action: self.start_rebinding(act))
            
            row_layout.addWidget(lbl)
            row_layout.addWidget(btn)
            self.shortcuts_layout.addWidget(row_widget)
            
        self.shortcuts_layout.addStretch()
        
        reset_btn = QPushButton("Reset to Default Shortcuts")
        reset_btn.clicked.connect(self.reset_hotkeys)
        self.shortcuts_layout.addWidget(reset_btn)

    def clear_sublayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_sublayout(child.layout())

    def start_rebinding(self, action):
        self.rebinding_action = action
        self.update_shortcuts_ui()

    def reset_hotkeys(self):
        self.hotkeys = {}
        for k, v in DEFAULT_HOTKEYS.items():
            self.hotkeys[k] = v.copy()
        self.save_settings()
        self.update_shortcuts_ui()

    def handle_rebinding_key(self, event):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            # Cancel rebinding
            self.rebinding_action = None
            self.update_shortcuts_ui()
            return
            
        # Convert event.key() and modifiers to string
        modifiers = event.modifiers()
        
        # Make sure we don't bind modifier-only presses
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return
            
        key_sequence = QKeySequence(key | modifiers.value)
        key_str = key_sequence.toString()
        
        if key_str:
            self.hotkeys[self.rebinding_action]["key"] = key_str
            self.rebinding_action = None
            self.save_settings()
            self.update_shortcuts_ui()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseMove:
            if self.isFullScreen():
                self.show_controls_in_fullscreen()
                
        if event.type() == QEvent.Type.KeyPress:
            # If we are in rebinding mode, capture the key press globally
            if self.rebinding_action is not None:
                self.handle_rebinding_key(event)
                return True # Consume it so the focused widget doesn't process it!
                
            # If the focused widget is a text input, bypass shortcuts to allow typing
            focused = QApplication.focusWidget()
            if isinstance(focused, (QLineEdit, QTextEdit, QPlainTextEdit)):
                return False
                
            key = event.key()
            
            # Allow native navigation and adjustments on lists and sliders
            # For QListWidget: only Up, Down, Enter, Return are native navigation. Left/Right should seek the video.
            if isinstance(focused, QListWidget) and key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Enter, Qt.Key.Key_Return):
                return False
            # For QSlider: allow native adjustment ONLY if it's NOT the main volume_slider or seekbar slider.
            if isinstance(focused, QSlider) and focused not in (self.volume_slider, self.slider):
                if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
                    return False
                
            # Otherwise, check if key_str matches any of our hotkeys
            modifiers = event.modifiers()
            if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
                return False
                
            # Filter modifiers to exclude NumLock, CapsLock, Keypad, etc. which break string matching
            clean_mods = Qt.KeyboardModifier.NoModifier
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                clean_mods |= Qt.KeyboardModifier.ShiftModifier
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                clean_mods |= Qt.KeyboardModifier.ControlModifier
            if modifiers & Qt.KeyboardModifier.AltModifier:
                clean_mods |= Qt.KeyboardModifier.AltModifier
            if modifiers & Qt.KeyboardModifier.MetaModifier:
                clean_mods |= Qt.KeyboardModifier.MetaModifier

            key_sequence = QKeySequence(key | clean_mods.value)
            key_str = key_sequence.toString()
            
            matched = False
            for action, data in self.hotkeys.items():
                if data["key"].lower() == key_str.lower():
                    self.trigger_shortcut_action(action)
                    matched = True
                    break
                    
            if matched:
                return True # Consume the event so standard widgets don't trigger native behaviors (e.g. Space clicking buttons)
                
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if self.rebinding_action is not None:
            self.handle_rebinding_key(event)
            return
        super().keyPressEvent(event)

    def trigger_shortcut_action(self, action):
        if action == "play_pause":
            self.toggle_play()
        elif action == "mute":
            self.toggle_mute()
        elif action == "fullscreen":
            self.toggle_fullscreen()
        elif action == "seek_back":
            self.seek_backward()
        elif action == "seek_fwd":
            self.seek_forward()
        elif action == "volume_up":
            curr = self.volume_slider.value()
            self.volume_slider.setValue(min(150, curr + 5))
        elif action == "volume_down":
            curr = self.volume_slider.value()
            self.volume_slider.setValue(max(0, curr - 5))
        elif action == "next_video":
            self.play_next()
        elif action == "prev_video":
            self.play_previous()
        elif action == "ab_loop":
            self.trigger_ab_loop()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.controls_hide_timer.stop()
            self.titlebar.show()
            self.sidebar.show()
            
            # Put controls back in layout
            self.controls_panel.setParent(self.video_area)
            self.video_area_layout.addWidget(self.controls_panel)
            self.controls_panel.show()
        else:
            self.showFullScreen()
            self.titlebar.hide()
            self.sidebar.hide()
            
            # Remove controls from layout and make it float
            self.video_area_layout.removeWidget(self.controls_panel)
            self.controls_panel.setParent(self)
            self.controls_panel.setGeometry(0, self.height() - 75, self.width(), 75)
            self.controls_panel.show()
            self.controls_panel.raise_()
            
            # Start timer
            self.controls_hide_timer.start()

    def show_controls_in_fullscreen(self):
        if not self.isFullScreen():
            return
            
        # Reset cursor and show controls
        self.setCursor(Qt.CursorShape.ArrowCursor)
        if self.controls_panel.parent() != self:
            self.controls_panel.setParent(self)
            self.controls_panel.setGeometry(0, self.height() - 75, self.width(), 75)
            self.controls_panel.show()
            self.controls_panel.raise_()
        elif self.controls_panel.isHidden():
            self.controls_panel.setGeometry(0, self.height() - 75, self.width(), 75)
            self.controls_panel.show()
            self.controls_panel.raise_()
            
        # Restart the 2-second auto-hide timer
        self.controls_hide_timer.start()

    def hide_controls_in_fullscreen(self):
        if self.isFullScreen():
            # If the user is currently hovering/interacting with controls, don't hide them
            if self.controls_panel.underMouse():
                # Postpone hide by another 2 seconds
                self.controls_hide_timer.start()
                return
                
            self.controls_panel.hide()
            self.setCursor(Qt.CursorShape.BlankCursor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.isFullScreen() and hasattr(self, "controls_panel") and self.controls_panel.parent() == self:
            self.controls_panel.setGeometry(0, self.height() - 75, self.width(), 75)

    # ==========================================================================
    # URL AND STREAM LOADER
    # ==========================================================================

    def open_url_dialog(self):
        url, ok = QInputDialog.getText(self, "Play Network Stream", "Enter stream or file URL:")
        if ok and url.strip():
            self.add_local_file(url.strip())

    # ==========================================================================
    # VIDEO ADJUSTMENT FILTERS
    # ==========================================================================

    def update_vlc_adjust_filter(self):
        if self.mpv_player:
            try:
                b_val = (self.brightness_slider.value() - 10) * 5
                c_val = (self.contrast_slider.value() - 10) * 5
                s_val = (self.saturation_slider.value() - 10) * 5
                h_val = float(self.hue_slider.value())
                self.mpv_player.brightness = int(b_val)
                self.mpv_player.contrast = int(c_val)
                self.mpv_player.saturation = int(s_val)
                self.mpv_player.hue = int(h_val)
            except Exception as e:
                print("Filter adjustment note:", e)
        
    def brightness_changed(self, value):
        val = value / 10.0
        self.brightness_val_lbl.setText(f"{val:.1f}")
        self.update_vlc_adjust_filter()
        
    def contrast_changed(self, value):
        val = value / 10.0
        self.contrast_val_lbl.setText(f"{val:.1f}")
        self.update_vlc_adjust_filter()
        
    def saturation_changed(self, value):
        val = value / 10.0
        self.saturation_val_lbl.setText(f"{val:.1f}")
        self.update_vlc_adjust_filter()
        
    def hue_changed(self, value):
        self.hue_val_lbl.setText(f"{value}°")
        self.update_vlc_adjust_filter()
        
    def reset_video_filters(self):
        self.brightness_slider.setValue(10)
        self.contrast_slider.setValue(10)
        self.saturation_slider.setValue(10)
        self.hue_slider.setValue(0)
        self.brightness_val_lbl.setText("1.0")
        self.contrast_val_lbl.setText("1.0")
        self.saturation_val_lbl.setText("1.0")
        self.hue_val_lbl.setText("0°")
        if self.mpv_player:
            self.mpv_player.brightness = 0; self.mpv_player.contrast = 0; self.mpv_player.saturation = 0; self.mpv_player.hue = 0

    # ==========================================================================
    # SUBTITLES CONTROLS
    # ==========================================================================

    def load_external_subtitle(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Subtitle File", "",
            "Subtitle files (*.srt *.vtt *.ass);;All files (*.*)"
        )
        if file_path and self.mpv_player:
            try:
                self.mpv_player.sub_add(file_path)
                self.sub_file_lbl.setText(os.path.basename(file_path))
                QTimer.singleShot(500, self.refresh_subtitle_tracks)
            except Exception as e:
                print("Failed to load subtitle:", e)
            
    def adjust_sub_delay(self, delta):
        if self.mpv_player:
            curr = self.mpv_player.sub_delay or 0.0
            new_val = curr + delta
            self.mpv_player.sub_delay = new_val
            self.sub_delay_lbl.setText(f"Delay Offset: {new_val:.1f}s")
        
    def reset_sub_delay(self):
        if self.mpv_player:
            self.mpv_player.sub_delay = 0.0
        self.sub_delay_lbl.setText("Delay Offset: 0.0s")
        
    def refresh_subtitle_tracks(self):
        self.sub_track_combo.blockSignals(True)
        self.sub_track_combo.clear()
        if self.mpv_player:
            try:
                tracks = self.mpv_player.track_list
                sub_count = 0
                for track in tracks:
                    if track.get('type') == 'sub':
                        sub_count += 1
                        t_id = track.get('id', 0)
                        title = track.get('title') or track.get('lang') or f"Track {t_id}"
                        self.sub_track_combo.addItem(title, t_id)
                        if track.get('selected'):
                            self.sub_track_combo.setCurrentIndex(self.sub_track_combo.count() - 1)
                if sub_count == 0:
                    self.sub_track_combo.addItem("No subtitle tracks found", -1)
            except Exception:
                self.sub_track_combo.addItem("No subtitle tracks found", -1)
        self.sub_track_combo.blockSignals(False)
        
    def sub_track_changed(self, index):
        track_id = self.sub_track_combo.itemData(index)
        if track_id is not None and track_id != -1 and self.mpv_player:
            self.mpv_player.sid = track_id

    # ==========================================================================
    # BOOKMARKS CONTROLS
    # ==========================================================================

    def add_bookmark(self):
        if self.current_index < 0 or self.current_index >= len(self.playlist):
            return
        video_path = self.playlist[self.current_index]
        title = self.bookmark_input.text().strip()
        if not title:
            title = "Marker"
            
        curr_time = int((self.mpv_player.time_pos or 0) * 1000) if self.mpv_player else 0
        if curr_time < 0:
            curr_time = 0
            
        if video_path not in self.bookmarks:
            self.bookmarks[video_path] = []
            
        self.bookmarks[video_path].append({"time": curr_time, "title": title})
        self.bookmarks[video_path].sort(key=lambda x: x["time"])
        
        self.bookmark_input.clear()
        self.save_settings()
        self.update_bookmarks_ui()
        
    def update_bookmarks_ui(self):
        self.bookmarks_list.clear()
        if self.current_index < 0 or self.current_index >= len(self.playlist):
            return
        video_path = self.playlist[self.current_index]
        video_bookmarks = self.bookmarks.get(video_path, [])
        
        for item in video_bookmarks:
            time_ms = item["time"]
            title = item["title"]
            
            secs = int(time_ms / 1000)
            time_str = f"{secs // 60:02d}:{secs % 60:02d}"
            
            list_item = QListWidgetItem(f"[{time_str}] - {title}")
            list_item.setData(Qt.ItemDataRole.UserRole, time_ms)
            self.bookmarks_list.addItem(list_item)
            
    def bookmark_clicked(self, item):
        time_ms = item.data(Qt.ItemDataRole.UserRole)
        if time_ms is not None and self.mpv_player:
            self.mpv_player.time_pos = time_ms / 1000.0
            
    def delete_bookmark(self):
        selected = self.bookmarks_list.currentRow()
        if selected < 0:
            return
        if self.current_index < 0 or self.current_index >= len(self.playlist):
            return
        video_path = self.playlist[self.current_index]
        video_bookmarks = self.bookmarks.get(video_path, [])
        if 0 <= selected < len(video_bookmarks):
            video_bookmarks.pop(selected)
            self.save_settings()
            self.update_bookmarks_ui()

    # ==========================================================================
    # LOCAL SCANNER LIBRARY CONTROLS
    # ==========================================================================

    def scan_folder_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Folder to Scan", "")
        if dir_path:
            self.scanned_folder = dir_path
            self.save_settings()
            self.rescan_library()
            
    def rescan_library(self):
        self.library_list.clear()
        if not getattr(self, "scanned_folder", ""):
            self.lib_path_lbl.setText("No active folder scanned")
            return
            
        dir_path = self.scanned_folder
        self.lib_path_lbl.setText(f"Folder: {dir_path}")
        
        if not os.path.exists(dir_path):
            self.lib_path_lbl.setText("❌ Folder not found!")
            return
            
        video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.ts', '.mp3', '.wav', '.flac')
        try:
            files = sorted(os.listdir(dir_path))
            for file in files:
                if file.lower().endswith(video_extensions):
                    full_path = os.path.join(dir_path, file)
                    list_item = QListWidgetItem(file)
                    list_item.setData(Qt.ItemDataRole.UserRole, full_path)
                    self.library_list.addItem(list_item)
                    self.request_thumbnail(full_path, list_item)
        except Exception as e:
            print("Failed to scan directory:", e)
            self.lib_path_lbl.setText("❌ Failed to scan directory")
            
    def library_item_clicked(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            self.add_local_file(file_path)
            if file_path in self.playlist:
                idx = self.playlist.index(file_path)
                self.load_video(idx)
                self.play_video()

    def open_buy_me_a_coffee(self):
        import webbrowser
        webbrowser.open("https://buymeacoffee.com/nemo7299")


# ==========================================================================
# MAIN EXECUTION ENTRY POINT
# ==========================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set global application font
    app.setFont(QFont("Segoe UI", 9))
    
    player = BingeBoxPlayer()
    player.show()
    sys.exit(app.exec())
