# -*- coding: utf-8 -*-

import codecs
import os
from typing import Dict, TextIO

from setuptools import find_packages, setup

pwd = os.path.abspath(os.path.dirname(__file__))

about: Dict[str, str] = {}

with codecs.open(os.path.join(pwd, "im", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

with open(file="README.md", mode="r") as r:  # type: TextIO
    readme = r.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    packages=find_packages(),
    package_dir={"im": "im"},
    include_package_data=True,
    license=about["__license__"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "pytz",
        "apscheduler",
        "SQLAlchemy",
        "prometheus_client",
        "icmplib",
        "PyYAML",
    ],
    entry_points="""
        [console_scripts]
        im=im.monitor:main
    """,
)
