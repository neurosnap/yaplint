# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="yaplint",
    version="1.0.0",
    description="yet another python linter",
    install_requires=["yaplint_core"],
    author='Eric Bower',
    author_email='neurosnap@gmail.com',
    url='https://github.com/neurosnap/yaplint',
    py_modules=["yaplint"],
    entry_points={
        "console_scripts": [
            "yaplint=yaplint:yaplint",
        ]
    }
)
