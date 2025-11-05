# NumSimGui

基于 PySide6 的图形用户界面应用程序。

## 功能特性

- 主窗口界面，包含菜单栏、工具栏、状态栏
- 多个可停靠窗口（Dock Widgets），支持拖拽和重新布局
- 中央工作区域

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

或者：

```bash
python -m src.NumSimGui.main
```

## 界面说明

应用程序包含以下组件：

1. **菜单栏**：File, Main window, Tool bars, Dock Widgets
2. **工具栏**：包含多个不同颜色的 Qt 按钮
3. **停靠窗口**：
   - 红色停靠窗口（顶部左侧）
   - 绿色停靠窗口（顶部右侧）
   - 黑色停靠窗口（左侧）
   - 白色停靠窗口（右侧）
   - 蓝色停靠窗口（底部左侧）
   - 黄色停靠窗口（底部右侧）
4. **中央区域**：空白工作区域
5. **状态栏**：显示状态信息

