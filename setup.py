from setuptools import setup, Extension

from Cython.Distutils import build_ext

import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

ext_modules = [
    Extension(
        'corridors.speedups',
        [
            "cython/speedups.pyx"
        ]
    )
]

setup(
    name='corridors',
    python_requires='>=3.5',
    author='Trevor Morgan',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
    packages=['corridors']
)

