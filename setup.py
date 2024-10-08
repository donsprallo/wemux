from setuptools import find_packages
from setuptools import setup


def load_requirements() -> list[str]:
    """Load project dependencies."""
    requirements = []
    with open('requirements.txt', 'r') as f:
        for line in f.readlines():
            # Skip comments and empty lines.
            if line.startswith('#') or line.isspace():
                continue
            requirements.append(line)
    return requirements


setup(
    name="wemux",
    version="0.0.1",
    description="A message bus.",
    author="donsprallo",
    author_email="donsprallo@gmail.com",
    packages=find_packages(include=[
        "wemux"
    ]),
    install_requires=load_requirements()
)
