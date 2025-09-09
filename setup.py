from pathlib import Path
from setuptools import setup, find_packages

README = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="Loubach",
    version="0.1.0",
    description="A Python toolkit for quantitative market analysis",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Phillip Korolev",
    author_email="p.korolev1@outlook.com",
    url="https://github.com/yourname/Loubach",
    license="MIT",
    packages=find_packages(exclude=("tests", "docs", "examples")),
    include_package_data=True,
    install_requires=[
        "numpy>=1.26.0",
        "pandas>=2.2.0",
        "matplotlib>=3.9.0",
        "seaborn>=0.13.0",
        "mplfinance>=0.12.10b0",
        "scipy>=1.13.0",
        "yfinance>=0.2.40",
        "plotly>=5.22.0",
    ],
    python_requires=">=3.9"
)