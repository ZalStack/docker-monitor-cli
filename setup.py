from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="docker-monitor-cli",
    version="1.0.0",
    author="DevOps Engineer",
    author_email="admin@example.com",
    description="Advanced Docker Resource Monitoring CLI Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/docker-monitor-cli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "docker>=6.1.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "psutil>=5.9.0",
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "docker-monitor=docker_monitor.cli:main",
        ],
    },
)