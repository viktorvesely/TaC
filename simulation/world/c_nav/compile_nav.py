from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy

extensions = [
    Extension("*", ["*.pyx"],
        include_dirs=[numpy.get_include()],)
]
setup(
    name="c_nav",
    ext_modules=cythonize(extensions),
)