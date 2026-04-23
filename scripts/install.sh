#!/bin/bash
# Installation script for Docker Monitor CLI on Fedora Linux

set -e

echo "🐳 Docker Monitor CLI Installation Script"
echo "========================================="

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION found"

# Check Docker installation
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   On Fedora: sudo dnf install docker"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker service."
    echo "   On Fedora: sudo systemctl start docker"
    exit 1
fi
echo "✅ Docker is running"

# Create virtual environment (optional)
if [ "$1" == "--venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install the package
echo "Installing Docker Monitor CLI..."
pip install -e .

# Add user to docker group if needed
if ! groups $USER | grep -q docker; then
    echo "⚠️  Note: You may need to add your user to the docker group:"
    echo "   sudo usermod -aG docker $USER"
    echo "   Then log out and back in for changes to take effect."
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  docker-monitor --help"
echo "  docker-monitor stats --watch"
echo "  docker-monitor list"
echo ""
echo "Try it out: docker-monitor stats --watch"