from setuptools import setup, find_packages

setup(
    name="jukebox",
    version="1.0.0",
    description="A music jukebox application built with pygame and SDL2",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "jukebox=src.main:main",
        ],
    },
)
