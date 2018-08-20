I've removed the Cython codebase and switched to pybind.

For reference, the Cython setup.py looked like this:

```python
from setuptools import setup, Extension

from Cython.Distutils import build_ext

from Cython.Build import cythonize
import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

ext_modules = [
    Extension(
        'corridors.speedups',
        [
            "cython/speedups.pyx"
        ],
        language="c++",
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

```