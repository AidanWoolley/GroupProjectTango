"""Setup.py file for tango module, which provides Linter and Validator."""
import setuptools

setuptools.setup(
    name="tango-r-assessor",
    version="1.0.0",
    author="Aidan Woolley",
    author_email="aw813@cam.ac.uk",
    description="An automatic assessor for R code",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
    python_requires='>=3.6'
)
