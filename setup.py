from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="claude-hook-master",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Parse and describe Claude Code hook inputs in plain English",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/claude-hook-master",
    packages=['src'],
    package_dir={'src': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "claude-hook-master=src.main:main",
            "chm=src.main:main",  # Short alias
        ],
    },
)