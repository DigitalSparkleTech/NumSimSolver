"""
NumSimGui 主程序入口
"""
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication

# 添加当前目录到路径，以便导入模块
sys.path.insert(0, str(Path(__file__).parent))

from main_window import MainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序全局样式，移除菜单阴影，添加悬停效果
    app.setStyleSheet("""
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
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

