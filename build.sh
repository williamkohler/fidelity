#!/bin/bash
# Build script for Render deployment
# This script installs system dependencies needed for audio support

echo "🔧 Installing system dependencies..."

# Update package list
apt-get update

# Install Python development headers and audio libraries
apt-get install -y \
    python3-dev \
    libasound2-dev \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
    libffi-dev \
    libssl-dev

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build completed successfully!" 