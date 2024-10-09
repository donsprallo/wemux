from setuptools import find_packages
from setuptools import setup


setup(
    name="wemux",
    version="0.0.1",
    description="A message bus.",
    author="donsprallo",
    author_email="donsprallo@gmail.com",
    packages=find_packages(include=[
        "wemux"
    ]),
    install_requires=[
        "pytest~=8.3",
        "pydantic~=2.9"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
