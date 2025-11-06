"""
NumSimGui 主窗口
基于 PySide6 的主窗口应用程序，包含多个可停靠窗口
"""
from PySide6.QtWidgets import (
    QMainWindow, QMenuBar, QStatusBar, QDockWidget,
    QWidget, QMessageBox, QFileDialog, QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QFormLayout, QScrollArea, QToolBar, QPushButton,
    QTabWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QColor, QAction, QKeySequence, QIcon, QPixmap
from pathlib import Path

# VTK 导入
try:
    from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    import vtk
    VTK_AVAILABLE = True
    
    # 创建自定义错误输出窗口来过滤关闭时的OpenGL错误
    class FilteredVTKOutputWindow(vtk.vtkOutputWindow):
        def __init__(self):
            super().__init__()
            self._closing = False
        
        def DisplayErrorText(self, text):
            # 如果正在关闭，忽略所有OpenGL相关错误
            if self._closing:
                if "wglMakeCurrent failed" in text or "句柄无效" in text or "error: 6" in text:
                    return
            # 正常情况下的错误仍然输出
            super().DisplayErrorText(text)
        
        def DisplayWarningText(self, text):
            # 警告也过滤关闭时的错误
            if self._closing:
                if "wglMakeCurrent failed" in text or "句柄无效" in text:
                    return
            super().DisplayWarningText(text)
        
        def DisplayGenericWarningText(self, text):
            if self._closing:
                if "wglMakeCurrent failed" in text or "句柄无效" in text:
                    return
            super().DisplayGenericWarningText(text)
        
        def DisplayDebugText(self, text):
            if self._closing:
                if "wglMakeCurrent failed" in text or "句柄无效" in text:
                    return
            super().DisplayDebugText(text)
        
        def set_closing(self, closing):
            self._closing = closing
    
    # 创建并设置自定义错误输出窗口
    _filtered_output = FilteredVTKOutputWindow()
    vtk.vtkOutputWindow.SetInstance(_filtered_output)
    
except ImportError:
    VTK_AVAILABLE = False
    print("警告: VTK 未安装，Visual View 将使用占位符")
    _filtered_output = None


class DelayedVTKWidget(QVTKRenderWindowInteractor if VTK_AVAILABLE else QWidget):
    """延迟初始化的VTK Widget"""
    
    def __init__(self, parent=None):
        if VTK_AVAILABLE:
            super().__init__(parent)
            self._vtk_initialized = False
            self._renderer = None
            self._actor = None
        else:
            QWidget.__init__(self, parent)
    
    def showEvent(self, event):
        """重写showEvent，延迟初始化VTK"""
        if VTK_AVAILABLE and not self._vtk_initialized:
            super().showEvent(event)
            # 使用QTimer延迟初始化，确保窗口完全显示
            QTimer.singleShot(100, self._initialize_vtk)
        else:
            if VTK_AVAILABLE:
                super().showEvent(event)
            else:
                QWidget.showEvent(self, event)
    
    def resizeEvent(self, event):
        """重写resizeEvent，更新VTK窗口大小"""
        if VTK_AVAILABLE and self._vtk_initialized:
            super().resizeEvent(event)
            if self.width() > 0 and self.height() > 0:
                try:
                    render_window = self.GetRenderWindow()
                    if render_window:
                        render_window.SetSize(self.width(), self.height())
                except:
                    pass
        else:
            if VTK_AVAILABLE:
                super().resizeEvent(event)
            else:
                QWidget.resizeEvent(self, event)
    
    def closeEvent(self, event):
        """重写closeEvent，清理VTK资源"""
        # 先标记为已关闭，防止后续操作
        self._vtk_initialized = False
        
        if VTK_AVAILABLE:
            try:
                # 停止交互（如果已初始化）
                if hasattr(self, 'Stop'):
                    try:
                        self.Stop()
                    except:
                        pass
                
                # 清理渲染窗口
                try:
                    render_window = self.GetRenderWindow()
                    if render_window:
                        # 禁用渲染窗口，避免后续操作
                        try:
                            # 设置窗口为未映射状态
                            render_window.SetMapped(0)
                            # 移除所有渲染器
                            render_window.RemoveAllRenderers()
                            # 禁用渲染
                            render_window.SetOffScreenRendering(1)
                            # 释放窗口资源
                            render_window.SetWindowId(None)
                        except:
                            pass
                except:
                    pass
            except Exception:
                # 忽略所有清理错误
                pass
        QWidget.closeEvent(self, event)
    
    def cleanup_vtk(self):
        """清理VTK资源（在窗口销毁前调用）"""
        if VTK_AVAILABLE and self._vtk_initialized:
            try:
                # 停止交互
                if hasattr(self, 'Stop'):
                    try:
                        self.Stop()
                    except:
                        pass
                
                # 清理渲染窗口
                try:
                    render_window = self.GetRenderWindow()
                    if render_window:
                        render_window.RemoveAllRenderers()
                        render_window.Finalize()
                except:
                    pass
                
                self._vtk_initialized = False
            except:
                pass
    
    def _initialize_vtk(self):
        """初始化VTK渲染"""
        if not VTK_AVAILABLE or self._vtk_initialized:
            return
        
        try:
            # 确保widget已经显示且大小有效
            if not self.isVisible() or self.width() <= 0 or self.height() <= 0:
                # 如果widget不可见或大小无效，再延迟一次
                QTimer.singleShot(100, self._initialize_vtk)
                return
            
            # 确保widget的父widget也已经显示（特别是tab widget）
            parent = self.parent()
            while parent:
                if hasattr(parent, 'isVisible') and not parent.isVisible():
                    QTimer.singleShot(100, self._initialize_vtk)
                    return
                parent = parent.parent()
            
            # 设置窗口大小
            if self.width() > 0 and self.height() > 0:
                self.GetRenderWindow().SetSize(self.width(), self.height())
            
            # 初始化交互（只在窗口完全准备好后）
            if not self._vtk_initialized:
                self.Initialize()
                self.Start()
                
                # 触发渲染
                self.GetRenderWindow().Render()
                
                self._vtk_initialized = True
        except Exception as e:
            print(f"警告: VTK初始化失败: {e}")
            # 如果初始化失败，标记为已初始化以避免无限重试
            self._vtk_initialized = True


class QtLogoWidget(QWidget):
    """显示 Qt 标志的组件"""
    
    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        self.color = color
        self.setMinimumSize(200, 200)
        
        # 根据背景颜色确定文字颜色
        # 如果是白色背景，使用黑色文字；否则使用与背景相同的颜色
        if color.red() == 255 and color.green() == 255 and color.blue() == 255:
            self.text_color = QColor(0, 0, 0)  # 白色背景用黑色文字
        else:
            self.text_color = color  # 其他颜色背景用相同颜色的文字
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), self.color)
        
        # 绘制 Qt 标志
        font = QFont("Arial", 72, QFont.Bold)
        painter.setFont(font)
        
        # 添加阴影效果
        shadow_color = QColor(0, 0, 0, 100)
        painter.setPen(shadow_color)
        painter.drawText(12, 122, "Qt")
        
        # 绘制主文字
        painter.setPen(self.text_color)
        painter.drawText(10, 120, "Qt")


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.current_file_path = None  # 当前打开的文件路径
        self.setting_view_dock = None  # Setting View dock widget
        self.config_dock = None  # 配置 dock widget
        self.setting_tree = None  # Setting View 中的树形控件
        self.visual_view_tab_widget = None  # Visual View tab widget
        self.visual_view_counter = 0  # Visual View 计数器（从1开始）
        # VTK 相关引用（存储所有VTK widget的引用）
        self.vtk_widgets = {}  # 存储每个Visual View的VTK widget
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("NumSimSolver")
        
        # 设置窗口图标
        self.set_window_icon()
        
        # 设置窗口大小
        window_width = 1200
        window_height = 800
        self.resize(window_width, window_height)
        
        # 将窗口移动到屏幕中央
        self.center_window()
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建中央区域（包含tab widget）
        self.create_central_widget()
        
        # 创建停靠窗口
        self.create_dock_widgets()
        
        # 创建状态栏
        self.create_status_bar()
        
    def set_window_icon(self):
        """设置窗口图标"""
        logo_path = Path(__file__).parent / "logo.png"
        if logo_path.exists():
            icon = QIcon(str(logo_path))
            self.setWindowIcon(icon)
        
    def center_window(self):
        """将窗口移动到屏幕中央"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        # 计算窗口应该放置的位置
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        
        self.move(x, y)
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 设置菜单栏样式，缩小菜单之间的间距，移除下拉菜单阴影
        menubar.setStyleSheet("""
            QMenuBar {
                spacing: 3px;
            }
            QMenuBar::item {
                padding: 4px 8px;
                spacing: 3px;
            }
            QMenu {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QMenu::item {
                padding: 4px 25px 4px 20px;
            }
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
            QMenu::item:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # 为整个应用程序设置菜单样式（移除阴影）
        self.setStyleSheet("""
            QMenu {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
            QMenu::item:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # File 菜单
        file_menu = menubar.addMenu("File")
        
        # 新建
        new_action = QAction("新建", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        # 打开
        open_action = QAction("打开", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # 保存
        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # 另存为
        save_as_action = QAction("另存为", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View 菜单
        view_menu = menubar.addMenu("View")
        
        # Setting View
        setting_view_action = QAction("Setting View", self)
        setting_view_action.triggered.connect(self.show_setting_view)
        view_menu.addAction(setting_view_action)
        
        # Visual View
        visual_view_action = QAction("Visual View", self)
        visual_view_action.triggered.connect(self.show_visual_view)
        view_menu.addAction(visual_view_action)
        
        # New Visual View
        new_visual_view_action = QAction("New Visual View", self)
        new_visual_view_action.triggered.connect(self.new_visual_view)
        view_menu.addAction(new_visual_view_action)
        
        # Help 菜单
        help_menu = menubar.addMenu("Help")
        help_action = help_menu.addAction("Help")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def new_file(self):
        """新建文件"""
        # TODO: 实现新建文件逻辑
        QMessageBox.information(self, "新建", "新建文件功能待实现")
        
    def open_file(self):
        """打开文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开文件",
            "",
            "所有文件 (*.*)"
        )
        if file_path:
            self.current_file_path = file_path
            # TODO: 实现打开文件逻辑
            self.statusBar().showMessage(f"已打开: {file_path}", 3000)
            
    def save_file(self):
        """保存文件"""
        if self.current_file_path:
            # TODO: 实现保存文件逻辑
            self.statusBar().showMessage(f"已保存: {self.current_file_path}", 3000)
        else:
            # 如果没有当前文件路径，调用另存为
            self.save_file_as()
            
    def save_file_as(self):
        """另存为"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "另存为",
            "",
            "所有文件 (*.*)"
        )
        if file_path:
            self.current_file_path = file_path
            # TODO: 实现保存文件逻辑
            self.statusBar().showMessage(f"已保存: {file_path}", 3000)
    
    def create_central_widget(self):
        """创建中央区域（包含 Visual View tab widget）"""
        # 创建 Tab Widget
        tab_widget = QTabWidget()
        tab_widget.setTabsClosable(True)  # 允许关闭标签
        tab_widget.setMovable(True)  # 允许拖拽标签
        tab_widget.tabCloseRequested.connect(self.close_visual_view_tab)
        tab_widget.currentChanged.connect(self.on_tab_changed)  # 监听tab切换
        
        # 创建第一个 Visual View
        self.visual_view_counter = 1
        first_view = self.create_visual_view_widget(view_id="Visual View")
        tab_widget.addTab(first_view, "Visual View")
        
        self.visual_view_tab_widget = tab_widget
        self.setCentralWidget(tab_widget)
    
    def on_tab_changed(self, index):
        """处理tab切换事件，确保VTK widget正确初始化"""
        if index < 0 or not self.visual_view_tab_widget:
            return
        
        widget = self.visual_view_tab_widget.widget(index)
        if widget and VTK_AVAILABLE:
            # 查找VTK widget
            vtk_widget = None
            for child in widget.findChildren(DelayedVTKWidget if VTK_AVAILABLE else QWidget):
                if isinstance(child, DelayedVTKWidget):
                    vtk_widget = child
                    break
            
            # 如果VTK widget存在但未初始化，触发初始化
            if vtk_widget and not getattr(vtk_widget, '_vtk_initialized', False):
                # 延迟触发初始化
                QTimer.singleShot(200, vtk_widget._initialize_vtk)
    
    def close_visual_view_tab(self, index):
        """关闭 Visual View tab"""
        if self.visual_view_tab_widget and self.visual_view_tab_widget.count() > 1:
            # 至少保留一个 tab
            widget = self.visual_view_tab_widget.widget(index)
            tab_title = self.visual_view_tab_widget.tabText(index)
            self.visual_view_tab_widget.removeTab(index)
            # 清理 VTK widget
            if widget:
                # 查找并清理 VTK widget引用
                if tab_title in self.vtk_widgets:
                    del self.vtk_widgets[tab_title]
                widget.deleteLater()
            
    def show_setting_view(self):
        """显示/隐藏设置视图"""
        if self.setting_view_dock:
            self.setting_view_dock.setVisible(not self.setting_view_dock.isVisible())
        
    def show_visual_view(self):
        """显示/隐藏可视化视图（现在通过tab widget显示）"""
        if self.visual_view_tab_widget:
            # Tab widget 始终显示，此方法不再需要
            pass
            
    def new_visual_view(self):
        """创建新的 Visual View tab"""
        if not self.visual_view_tab_widget:
            return
        
        self.visual_view_counter += 1
        title = f"Visual View {self.visual_view_counter}"
        
        # 创建新的 Visual View widget
        view_widget = self.create_visual_view_widget(view_id=title)
        
        # 添加到 tab widget
        self.visual_view_tab_widget.addTab(view_widget, title)
        
        # 切换到新创建的 tab
        self.visual_view_tab_widget.setCurrentIndex(self.visual_view_tab_widget.count() - 1)
            
    def show_help(self):
        """显示帮助对话框"""
        QMessageBox.information(
            self,
            "Help",
            "帮助文档"
        )
            
    def show_about(self):
        """显示关于对话框"""
        logo_path = Path(__file__).parent / "logo.png"
        
        if logo_path.exists():
            # 创建关于对话框，包含 logo
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("About")
            msg_box.setText("NumSimSolver")
            msg_box.setInformativeText("数值模拟求解器图形界面")
            
            # 加载并设置 logo
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                # 缩放 logo 到合适大小（例如 64x64）
                scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                msg_box.setIconPixmap(scaled_pixmap)
            
            msg_box.exec()
        else:
            # 如果 logo 不存在，使用默认的 about 对话框
            QMessageBox.about(
                self,
                "About",
                "NumSimSolver\n\n"
                "数值模拟求解器图形界面"
            )
            
    def create_dock_widgets(self):
        """创建停靠窗口"""
        # Setting View dock widget（左侧）
        self.setting_view_dock = self.create_setting_view_dock()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.setting_view_dock)
        
        # 设置 Setting View 的最小和最大宽度（允许调整大小）
        self.setting_view_dock.setMinimumWidth(200)
        self.setting_view_dock.setMaximumWidth(380)
        # 设置初始宽度
        self.setting_view_dock.resize(300, self.setting_view_dock.height())
        
        # 创建配置 dock widget（初始隐藏，点击叶子节点时显示）
        self.config_dock = self.create_config_dock()
        # 使用 splitDockWidget 来确保可以调整大小
        self.splitDockWidget(self.setting_view_dock, self.config_dock, Qt.Vertical)
        self.config_dock.setVisible(False)  # 初始隐藏
        
    def create_setting_view_dock(self) -> QDockWidget:
        """创建 Setting View 停靠窗口（带树形控件）"""
        dock = QDockWidget("Setting View", self)
        dock.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea |
            Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea
        )
        
        # 创建内容组件容器
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建树形控件
        tree = QTreeWidget()
        tree.setHeaderHidden(True)  # 隐藏 header
        tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: none;
            }
        """)
        
        # 保存树形控件引用，以便后续使用
        self.setting_tree = tree
        
        # 连接树形控件的点击事件
        tree.itemClicked.connect(self.on_tree_item_clicked)
        
        # 添加一些示例节点
        root_item = tree.invisibleRootItem()
        
        # 添加示例分类
        category1 = QTreeWidgetItem(tree, ["General"])
        category2 = QTreeWidgetItem(tree, ["Solver"])
        category3 = QTreeWidgetItem(tree, ["Mesh"])
        
        # 添加示例子项（叶子节点）
        QTreeWidgetItem(category1, ["Setting 1"])
        QTreeWidgetItem(category1, ["Setting 2"])
        QTreeWidgetItem(category2, ["Setting 3"])
        QTreeWidgetItem(category2, ["Setting 4"])
        QTreeWidgetItem(category3, ["Setting 5"])
        
        # 展开所有节点
        tree.expandAll()
        
        layout.addWidget(tree)
        container.setLayout(layout)
        dock.setWidget(container)
        
        return dock
    
    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """处理树形控件节点点击事件"""
        # 检查是否为叶子节点（没有子节点）
        if item.childCount() == 0:
            # 显示配置 dock widget
            if self.config_dock:
                self.config_dock.setVisible(True)
                # 更新配置项内容
                self.update_config_widget(item.text(0))
        else:
            # 如果是父节点，隐藏配置 dock widget
            if self.config_dock:
                self.config_dock.setVisible(False)
    
    def create_config_dock(self) -> QDockWidget:
        """创建配置 dock widget"""
        dock = QDockWidget("Configuration", self)
        dock.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea |
            Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea
        )
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        # 创建配置内容容器
        config_widget = QWidget()
        config_widget.setStyleSheet("background-color: white;")
        self.config_form_layout = QFormLayout()
        self.config_form_layout.setSpacing(10)
        self.config_form_layout.setContentsMargins(10, 10, 10, 10)
        config_widget.setLayout(self.config_form_layout)
        
        scroll_area.setWidget(config_widget)
        dock.setWidget(scroll_area)
        
        # 设置最小和最大宽度（允许调整大小，与 Setting View 对齐）
        dock.setMinimumWidth(200)
        dock.setMaximumWidth(380)
        # 设置初始宽度
        dock.resize(300, dock.height())
        
        dock.setMinimumHeight(200)
        # dock.setMaximumHeight(400)

        # 设置初始高度
        dock.resize(dock.width(), 350)
        
        return dock
    
    def update_config_widget(self, setting_name: str):
        """更新配置 widget 的内容"""
        # 清除现有内容
        while self.config_form_layout.count():
            child = self.config_form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 根据设置名称创建不同的配置项
        # 这里可以根据实际需求自定义配置项
        
        # 示例：添加一些通用配置项
        name_label = QLabel("Setting Name:")
        name_value = QLabel(setting_name)
        name_value.setStyleSheet("font-weight: bold;")
        self.config_form_layout.addRow(name_label, name_value)
        
        # 添加示例配置项
        value_label = QLabel("Value:")
        value_input = QLineEdit()
        value_input.setPlaceholderText("Enter value...")
        self.config_form_layout.addRow(value_label, value_input)
        
        numeric_label = QLabel("Numeric Value:")
        numeric_input = QDoubleSpinBox()
        numeric_input.setRange(0.0, 1000.0)
        numeric_input.setValue(0.0)
        numeric_input.setDecimals(2)
        self.config_form_layout.addRow(numeric_label, numeric_input)
        
        option_label = QLabel("Option:")
        option_combo = QComboBox()
        option_combo.addItems(["Option 1", "Option 2", "Option 3"])
        self.config_form_layout.addRow(option_label, option_combo)
        
        # 添加一个分隔符（空白行）
        self.config_form_layout.addRow(QLabel(""), QLabel(""))
        
    
    def create_visual_view_widget(self, view_id=None) -> QWidget:
        """创建 Visual View 组件（包含工具条和 VTK 视图）"""
        # 创建主容器
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建顶部工具条
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f0f0f0;
                border: none;
                border-bottom: 1px solid #c0c0c0;
                spacing: 5px;
                padding: 5px;
            }
            QPushButton {
                padding: 5px 10px;
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # 添加工具条按钮（连接到当前view_id对应的VTK widget）
        # 使用默认参数避免lambda闭包问题
        reset_view_btn = QPushButton("Reset View")
        reset_view_btn.clicked.connect(lambda checked, vid=view_id: self.reset_vtk_view_by_id(vid))
        toolbar.addWidget(reset_view_btn)
        
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(lambda checked, vid=view_id: self.zoom_in_vtk_view_by_id(vid))
        toolbar.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(lambda checked, vid=view_id: self.zoom_out_vtk_view_by_id(vid))
        toolbar.addWidget(zoom_out_btn)
        
        toolbar.addSeparator()
        
        wireframe_btn = QPushButton("Wireframe")
        wireframe_btn.clicked.connect(lambda checked, vid=view_id: self.toggle_wireframe_by_id(vid))
        toolbar.addWidget(wireframe_btn)
        
        # 创建 VTK 视图区域
        if VTK_AVAILABLE:
            vtk_widget = DelayedVTKWidget()
            self.setup_vtk_widget(vtk_widget, view_id)
        else:
            # 如果 VTK 不可用，创建占位符
            vtk_widget = QWidget()
            vtk_widget.setStyleSheet("background-color: #2b2b2b;")
            placeholder_label = QLabel("VTK View\n(VTK not installed)")
            placeholder_label.setAlignment(Qt.AlignCenter)
            placeholder_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 16px;
                    background-color: transparent;
                }
            """)
            placeholder_layout = QVBoxLayout()
            placeholder_layout.addWidget(placeholder_label)
            vtk_widget.setLayout(placeholder_layout)
        
        # 添加到布局
        layout.addWidget(toolbar)
        layout.addWidget(vtk_widget, 1)  # 设置拉伸因子为1，占据剩余空间
        
        container.setLayout(layout)
        return container
    
    def setup_vtk_widget(self, vtk_widget, view_id=None):
        """设置VTK widget的渲染内容"""
        if not VTK_AVAILABLE:
            return
        
        # 创建 VTK 渲染器
        renderer = vtk.vtkRenderer()
        renderer.SetBackground(0.2, 0.2, 0.2)  # 深灰色背景
        
        # 创建示例几何体（一个球体）
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(1.0)
        sphere.SetThetaResolution(50)
        sphere.SetPhiResolution(50)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.8, 0.8, 0.8)  # 浅灰色
        
        renderer.AddActor(actor)
        renderer.ResetCamera()
        
        # 设置渲染器
        vtk_widget.GetRenderWindow().AddRenderer(renderer)
        
        # 保存引用以便后续使用
        vtk_widget._renderer = renderer
        vtk_widget._actor = actor
        
        # 存储到字典中
        if view_id is None:
            view_id = f"view_{len(self.vtk_widgets)}"
        self.vtk_widgets[view_id] = {
            'widget': vtk_widget,
            'renderer': renderer,
            'actor': actor
        }
        
        # 为了向后兼容，也设置current_*引用（指向第一个）
        if not hasattr(self, 'current_vtk_widget') or self.current_vtk_widget is None:
            self.current_vtk_widget = vtk_widget
            self.current_vtk_renderer = renderer
            self.current_vtk_actor = actor
    
    def get_current_vtk_data(self, view_id=None):
        """获取指定view_id的VTK数据，如果没有指定则使用当前激活的tab"""
        if view_id and view_id in self.vtk_widgets:
            return self.vtk_widgets[view_id]
        
        # 如果没有指定view_id，使用当前激活的tab
        if self.visual_view_tab_widget:
            current_index = self.visual_view_tab_widget.currentIndex()
            if current_index >= 0:
                current_tab_title = self.visual_view_tab_widget.tabText(current_index)
                if current_tab_title in self.vtk_widgets:
                    return self.vtk_widgets[current_tab_title]
        
        # 如果都没有，返回第一个
        if self.vtk_widgets:
            return next(iter(self.vtk_widgets.values()))
        
        return None
    
    def reset_vtk_view(self):
        """重置 VTK 视图（使用当前激活的tab）"""
        vtk_data = self.get_current_vtk_data()
        if vtk_data:
            vtk_data['renderer'].ResetCamera()
            vtk_data['widget'].GetRenderWindow().Render()
    
    def reset_vtk_view_by_id(self, view_id):
        """根据view_id重置VTK视图"""
        vtk_data = self.get_current_vtk_data(view_id)
        if vtk_data:
            vtk_data['renderer'].ResetCamera()
            vtk_data['widget'].GetRenderWindow().Render()
    
    def zoom_in_vtk_view(self):
        """放大 VTK 视图（使用当前激活的tab）"""
        vtk_data = self.get_current_vtk_data()
        if vtk_data:
            camera = vtk_data['renderer'].GetActiveCamera()
            camera.Zoom(1.2)
            vtk_data['widget'].GetRenderWindow().Render()
    
    def zoom_in_vtk_view_by_id(self, view_id):
        """根据view_id放大VTK视图"""
        vtk_data = self.get_current_vtk_data(view_id)
        if vtk_data:
            camera = vtk_data['renderer'].GetActiveCamera()
            camera.Zoom(1.2)
            vtk_data['widget'].GetRenderWindow().Render()
    
    def zoom_out_vtk_view(self):
        """缩小 VTK 视图（使用当前激活的tab）"""
        vtk_data = self.get_current_vtk_data()
        if vtk_data:
            camera = vtk_data['renderer'].GetActiveCamera()
            camera.Zoom(0.8)
            vtk_data['widget'].GetRenderWindow().Render()
    
    def zoom_out_vtk_view_by_id(self, view_id):
        """根据view_id缩小VTK视图"""
        vtk_data = self.get_current_vtk_data(view_id)
        if vtk_data:
            camera = vtk_data['renderer'].GetActiveCamera()
            camera.Zoom(0.8)
            vtk_data['widget'].GetRenderWindow().Render()
    
    def toggle_wireframe(self):
        """切换线框模式（使用当前激活的tab）"""
        vtk_data = self.get_current_vtk_data()
        if vtk_data and VTK_AVAILABLE:
            prop = vtk_data['actor'].GetProperty()
            if prop.GetRepresentation() == vtk.VTK_SURFACE:
                prop.SetRepresentation(vtk.VTK_WIREFRAME)
            else:
                prop.SetRepresentation(vtk.VTK_SURFACE)
            vtk_data['widget'].GetRenderWindow().Render()
    
    def toggle_wireframe_by_id(self, view_id):
        """根据view_id切换线框模式"""
        vtk_data = self.get_current_vtk_data(view_id)
        if vtk_data and VTK_AVAILABLE:
            prop = vtk_data['actor'].GetProperty()
            if prop.GetRepresentation() == vtk.VTK_SURFACE:
                prop.SetRepresentation(vtk.VTK_WIREFRAME)
            else:
                prop.SetRepresentation(vtk.VTK_SURFACE)
            vtk_data['widget'].GetRenderWindow().Render()
        
    def create_status_bar(self):
        """创建状态栏"""
        statusbar = QStatusBar()
        statusbar.showMessage("Status Bar")
        self.setStatusBar(statusbar)
    
    def closeEvent(self, event):
        """重写closeEvent，在关闭窗口前清理所有VTK资源"""
        # 设置VTK错误输出为关闭状态，忽略关闭时的错误
        if VTK_AVAILABLE and _filtered_output:
            try:
                _filtered_output.set_closing(True)
            except:
                pass
        
        # 先隐藏窗口，避免VTK在窗口关闭时尝试渲染
        self.hide()
        
        # 清理所有VTK widget
        if VTK_AVAILABLE and hasattr(self, 'vtk_widgets'):
            for view_id, vtk_data in list(self.vtk_widgets.items()):
                try:
                    vtk_widget = vtk_data.get('widget')
                    if vtk_widget and hasattr(vtk_widget, '_vtk_initialized'):
                        # 先标记为未初始化，阻止后续操作
                        vtk_widget._vtk_initialized = False
                        
                        try:
                            # 停止交互
                            if hasattr(vtk_widget, 'Stop'):
                                vtk_widget.Stop()
                        except:
                            pass
                        
                        # 清理渲染窗口（禁用所有操作）
                        try:
                            render_window = vtk_widget.GetRenderWindow()
                            if render_window:
                                # 设置窗口为未映射状态
                                try:
                                    render_window.SetMapped(0)
                                except:
                                    pass
                                
                                # 禁用渲染
                                try:
                                    render_window.SetOffScreenRendering(1)
                                except:
                                    pass
                                
                                # 移除所有渲染器
                                try:
                                    render_window.RemoveAllRenderers()
                                except:
                                    pass
                                
                                # 释放窗口ID
                                try:
                                    render_window.SetWindowId(None)
                                except:
                                    pass
                        except:
                            pass
                except Exception:
                    # 忽略清理时的错误，避免影响窗口关闭
                    pass
        
        # 清空VTK widgets字典
        if hasattr(self, 'vtk_widgets'):
            self.vtk_widgets.clear()
        
        # 调用父类的closeEvent
        super().closeEvent(event)
        
        # 恢复VTK错误输出（虽然窗口已经关闭）
        if VTK_AVAILABLE and _filtered_output:
            try:
                _filtered_output.set_closing(False)
            except:
                pass

