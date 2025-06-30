from setuptools import setup, find_packages

setup(
    name="life360",
    version="7.0.1",
    packages=find_packages(
        include=["life360", "life360.*"]
    ),
    install_requires=[],
    python_requires=">=3.8",
)
