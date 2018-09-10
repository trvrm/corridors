from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools
import pybind11

__version__ = '0.0.3'


ext_modules = [
    Extension(
        'corridors._corridors',
        ['src/main.cpp','src/board.cpp', 'src/bots.cpp'],
        include_dirs=[
            # Path to pybind11 headers
            pybind11.get_include(user=False),
            pybind11.get_include(user=True)
        ],
        language='c++'
    ),
    Extension(
        'corridors._corridors_mcts',
        ['src/mcts/board.cpp','src/mcts/corridors_threaded_api.cpp', 'src/mcts/_corridors_mcts.cpp'],
        include_dirs=[sys.prefix + '/include/python3.6m'],
        libraries = ['boost_python3-py36','boost_numpy3-py36'],
        language='c++',
    )
]

class BuildExt(build_ext):
    """
        I only support linux  :-)
    """

    def build_extensions(self):
        opts = []
        opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
        # opts.append(cpp_flag(self.compiler))
        # if has_flag(self.compiler, '-fvisibility=hidden'):
        #     opts.append('-fvisibility=hidden')

        # add/remove compiler flags
        remove_flags = ['-Wall','-g','-O2','-Wstrict-prototypes']
        add_flags = ['-Ofast','-Wno-attributes']

        self.compiler.compiler_so = [f for f in self.compiler.compiler_so if f not in remove_flags]
        self.compiler.compiler_so.extend(add_flags)

        for ext in self.extensions:
            ext.extra_compile_args = opts
        super(BuildExt, self).build_extensions()


setup(
    name='corridors',
    version=__version__,
    author='Trevor Morgan',
    description='Corridors, using pybind11',
    cmdclass={'build_ext': BuildExt},
    ext_modules=ext_modules,
    packages=['corridors']
)