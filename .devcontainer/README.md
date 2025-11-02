# VS Code Dev Container Setup

This project now includes a VS Code Development Container configuration that provides a consistent, reproducible development environment.

## Prerequisites

1. **VS Code** with the **Dev Containers** extension installed
2. **Docker** or **Podman** installed and running on your system

## Getting Started

### Option 1: Open in VS Code Dev Container (Recommended)

1. Open the project folder in VS Code
2. When prompted, click "Reopen in Container" or:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Dev Containers: Reopen in Container"
   - Press Enter

VS Code will automatically:
- Build the Docker container
- Install all Python dependencies
- Set up the development environment
- Install the package in development mode

### Option 2: Manual Container Build

If you prefer to build manually:

```bash
# Build the development container using the main Dockerfile
docker build --target development -t gedcom-visualizer-dev .
docker run -it -v "$(pwd)":/workspace gedcom-visualizer-dev
```

## What's Included

The dev container includes:

### System Tools
- Python 3.12
- Git, vim, nano, curl, wget
- Build essentials
- Bash shell

### Python Packages
- All packages from `requirements.txt`
- Development tools: pylint, black, flake8, pytest
- Interactive tools: ipython, jupyter

### VS Code Extensions
- Python extension with linting and formatting
- JSON and YAML support
- Git integration

## Available Tasks

Once in the container, you can use VS Code tasks (Ctrl+Shift+P → "Tasks: Run Task"):

- **Install Package in Development Mode**: Installs the package for development
- **List GEDCOM File**: Lists all individuals in a GEDCOM file
- **Search GEDCOM File**: Search for individuals by name
- **Validate GEDCOM File**: Validate GEDCOM format
- **Run Tests**: Execute pytest
- **Format Code**: Format code with Black
- **Lint Code**: Check code with Pylint

## Debug Configurations

Pre-configured debug sessions are available:

- **Debug GEDCOM List**: Debug the list functionality
- **Debug GEDCOM Search**: Debug the search functionality  
- **Debug GEDCOM Validation**: Debug GEDCOM validation

## Usage Examples

### List all individuals in a GEDCOM file:
```bash
python -m gedcom_visualizer.list_search MyHeritage_export_2025-11-02.ged
```

### Search for individuals:
```bash
python -m gedcom_visualizer.list_search MyHeritage_export_2025-11-02.ged -s "Johan"
```

### Validate GEDCOM format:
```bash
python -m gedcom_visualizer.validate_gedcom MyHeritage_export_2025-11-02.ged
```

## Container Features

- **Automatic setup**: Dependencies are installed when the container starts
- **Volume mounting**: Your local workspace is mounted in the container
- **Port forwarding**: Ready for web applications (if needed)
- **Git integration**: Git credentials are forwarded from host
- **Terminal access**: Full bash terminal access

## Troubleshooting

### Container won't start
- Ensure Docker/Podman is running
- Check if the port is already in use
- Try rebuilding: "Dev Containers: Rebuild Container"

### Python import errors
- Run the "Install Package in Development Mode" task
- Check that you're in the `/workspace` directory
- Verify PYTHONPATH is set correctly

### GEDCOM parsing errors
The improved parser handles common MyHeritage export format violations automatically.

## File Structure

```
Dockerfile                    # Main multi-stage Dockerfile (base, development, production)
.devcontainer/
└── devcontainer.json        # Dev container configuration (uses main Dockerfile)

.vscode/
├── settings.json           # VS Code workspace settings  
├── tasks.json             # Predefined tasks
└── launch.json            # Debug configurations
```

## Architecture

The project uses a multi-stage Dockerfile approach:

- **Base stage**: Common dependencies (Python, LaTeX, core packages)
- **Development stage**: Adds dev tools, VS Code extensions, debugging tools
- **Production stage**: Optimized for DistroBox and production deployment

The devcontainer uses the **development** stage, while the production container (for DistroBox) uses the **production** stage.

## Benefits of Using Dev Containers

1. **Consistency**: Same environment for all developers
2. **Isolation**: No conflicts with host system packages
3. **Reproducibility**: Exact same setup every time
4. **Easy onboarding**: New developers can start immediately
5. **Tool integration**: All development tools pre-configured

---

For more information about VS Code Dev Containers, see: https://code.visualstudio.com/docs/devcontainers/containers
