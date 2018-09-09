from distutils.core import setup, Extension


gridCut3D = Extension('_gridCut3D', sources=['gridCut3D.cpp', 'gridCut3D_wrap.cxx'], swig_opts=['-c++'])

setup(name='gridCut3D',
       version = '0.1',
       author      = "V",
       description = """Grid cuts""",
       ext_modules = [gridCut3D],
       py_modules = ["gridCut3D"],
)
