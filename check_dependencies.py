#!/usr/bin/env python3
"""
Dependency verification script for GEDCOM Visualizer.

This script checks that all required dependencies are properly installed
and working in the current environment.
"""

import sys
import subprocess
import importlib


def check_python_package(package_name, import_name=None):
    """Check if a Python package is available."""
    if import_name is None:
        import_name = package_name

    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name}: Available")
        return True
    except ImportError:
        print(f"❌ {package_name}: Not available")
        return False


def check_system_command(command, package_name=None):
    """Check if a system command is available."""
    if package_name is None:
        package_name = command

    try:
        result = subprocess.run(
            [command, "--version"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            version = result.stdout.strip().split("\n")[0]
            print(f"✅ {package_name}: {version}")
            return True
        else:
            print(f"❌ {package_name}: Command failed")
            return False
    except FileNotFoundError:
        print(f"❌ {package_name}: Command not found")
        return False


def check_graphviz_special():
    """Special check for Graphviz dot command."""
    try:
        result = subprocess.run(
            ["dot", "-V"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            # Graphviz outputs version to stderr
            version = result.stderr.strip()
            print(f"✅ Graphviz: {version}")
            return True
        else:
            print("❌ Graphviz: Command failed")
            return False
    except FileNotFoundError:
        print("❌ Graphviz: Command not found")
        return False


def main():
    """Run all dependency checks."""
    print("🔍 GEDCOM Visualizer Dependency Check")
    print("=" * 40)

    all_good = True

    print("\n📦 Python Packages:")
    all_good &= check_python_package("gedcom")
    all_good &= check_python_package("sphinx")
    all_good &= check_python_package("sphinx_rtd_theme")
    all_good &= check_python_package("sphinx.ext.graphviz", "sphinx.ext.graphviz")

    print("\n🖥️  System Commands:")
    all_good &= check_system_command("python3", "Python 3")
    all_good &= check_system_command("pdflatex", "LaTeX")
    all_good &= check_system_command("sphinx-build", "Sphinx CLI")
    all_good &= check_graphviz_special()

    print("\n" + "=" * 40)
    if all_good:
        print("🎉 All dependencies are available!")
        print("✅ GEDCOM Visualizer is ready to use.")
        sys.exit(0)
    else:
        print("⚠️  Some dependencies are missing.")
        print("❌ Please install missing dependencies or use the dev container.")
        sys.exit(1)


if __name__ == "__main__":
    main()
