# NumSimSolver

**A comprehensive numerical simulation solver with modern GUI interface**

NumSimSolver is an integrated numerical simulation software platform designed for engineering and scientific computing. It provides a user-friendly graphical interface for setting up, configuring, and visualizing numerical simulations, with support for mesh import/export and advanced 3D visualization capabilities.

## Overview

NumSimSolver combines a powerful C++ computational core with a modern Python-based graphical user interface, offering a complete solution for numerical simulation workflows. The application features a flexible dockable window system, interactive 3D visualization, and an intuitive configuration management system.

## Features

### Core Components

- **NumSimCore**: High-performance C++ computational engine for numerical simulations
- **NumSimGui**: Modern PySide6-based graphical user interface with:
  - Dockable window system for flexible workspace layout
  - Setting View with hierarchical tree structure for parameter configuration
  - Visual View with VTK-based 3D rendering and interactive tools
  - Configuration panel for detailed parameter editing
- **NumSimMeshImport/Export**: Mesh data import and export utilities
- **NumSimSolver**: Numerical solver engine

### Key Features

- **Interactive 3D Visualization**: VTK-powered rendering with zoom, pan, rotate, and wireframe mode
- **Hierarchical Configuration**: Tree-based settings organization with dynamic configuration panels
- **Flexible UI Layout**: Resizable dock widgets that can be arranged according to user preferences
- **Project Management**: File operations for saving and loading simulation projects
- **Multi-View Support**: Create and manage multiple visualization views simultaneously

## Technology Stack

- **GUI Framework**: PySide6 (Qt for Python)
- **3D Visualization**: VTK (Visualization Toolkit)
- **Core Language**: C++ (for computational performance)
- **Scripting**: Python 3.12+
- **Dependencies**: NumPy, Pillow

## Status

🚧 **This project is under active development.** 🚧

NumSimSolver is currently in active development. New features, improvements, and bug fixes are being added regularly. The API and user interface may change as the project evolves.

### Current Development Status

- ✅ Core GUI framework implemented
- ✅ Basic 3D visualization with VTK
- ✅ Configuration management system
- ✅ Dock widget system
- 🚧 Advanced solver integration (in progress)
- 🚧 Mesh import/export functionality (in progress)
- 🚧 Documentation and tutorials (in progress)

## Installation

### Prerequisites

- Python 3.12 or higher
- CMake 3.10 or higher (for C++ components)
- C++ compiler with C++17 support

### Python Dependencies

```bash
pip install -r src/NumSimGui/requirements.txt
```

Required packages:
- PySide6 >= 6.5.0
- VTK >= 9.0.0
- Pillow >= 10.0.0
- NumPy >= 1.20.0

## Getting Started

### Running the GUI Application

```bash
cd src/NumSimGui
python main.py
```

## License

This project is licensed under the LGPL v3 License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

Contributions are welcome! Since this project is under active development, please feel free to submit issues, feature requests, or pull requests.

## Project Structure

```
numsimsolver/
├── src/
│   ├── NumSimCore/          # C++ computational core
│   ├── NumSimGui/           # Python GUI application
│   ├── NumSimMeshImport/    # Mesh import utilities
│   ├── NumSimMeshExport/    # Mesh export utilities
│   └── NumSimSolver/        # Numerical solver engine
├── doc/                     # Documentation
└── tutorials/               # Tutorial materials
```

---

**Note**: This project is actively being developed. Please check back regularly for updates and new features.
