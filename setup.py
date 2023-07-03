"""
"""

from setuptools import setup, find_packages

setup_requires = []
install_requires = ["nltk"]

classifiers = ["Intended Audience :: Science/Research",
               "Operating System :: OS Independent",
               "Programming Language :: Python :: 3"]

setup(
    name="ads2bibtex",
    version="0.1.dev",
    author="Yoonsoo P. Bach",
    author_email="ysbach93@gmail.com",
    description="",
    license="BSD-3",
    keywords="",
    url="",
    classifiers=classifiers,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ads2bibtex = ads2bibtex.scripts.ads2bib:main'
        ]
    },
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=install_requires
)
