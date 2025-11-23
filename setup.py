from setuptools import find_packages, setup

setup(
    name="jukebox",
    version="0.1.0",
    description="A music jukebox application built with pygame and SDL2",
    author="Jeremy Wininger",
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
