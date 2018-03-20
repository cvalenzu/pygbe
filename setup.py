import sys
import os
from distutils.command.build import build
from distutils.command.clean import clean
from setuptools.command.install import install
from setuptools import setup, find_packages, Extension
import numpy
import shutil
import versioneer
from Cython.Build import cythonize

class CustomBuild(build):
    """
    Subclasses build command to ensure that built_ext is run before files
    are copied.  Make setuptools compile the Cython files first, then run install
    """
    def run(self):
        self.run_command('build_ext')
        build.run(self)

class CustomInstall(install):
    """
    Subclasses install command to ensure that built_ext is run before files
    are copied.  Make setuptools compile the Cython files first, then run install
    """
    def run(self):
        self.run_command('build_ext')
        self.do_egg_install()
        #setuptools cleanup is weak, do it manually
        cmdline = ''.join(sys.argv[1:])
        if 'clean' in cmdline:
            for tree in ['PyGBe.egg-info', 'build', 'dist']:
                shutil.rmtree(tree, ignore_errors=True)
            for cyfile in [
                    'pygbe/tree/calculateMultipoles.py',
                    'pygbe/tree/calculateMultipoles_wrap.cpp',
                    'pygbe/tree/direct.py',
                    'pygbe/tree/direct_wrap.cpp',
                    'pygbe/tree/multipole.py',
                    'pygbe/tree/multipole_wrap.cpp',
                    'pygbe/util/semi_analyticalwrap.py',
                    'pygbe/util/semi_analyticalwrap_wrap.cpp',]:
                os.remove(cyfile)

def main():
    setupkw = dict(
            name='PyGBe',
            description='A boundary element method code that does molecular electrostatics calculations with a continuum approach',
            platforms='Linux',
            install_requires = ['numpy > 1.8',],
            license='MIT',
            version=versioneer.get_version(),
            cmdclass=versioneer.get_cmdclass(cmdclass={'build': CustomBuild, 'install': CustomInstall}),
            url='https://github.com/barbagroup/pygbe',
            classifiers=['Programming Language :: Python :: 3'],
            packages = find_packages(),
            #tell setuptools to use the custom build and install classes
            #create an entrance point that points to pygbe.main.main
            entry_points={'console_scripts': ['pygbe = pygbe.main:main',
                                              'pygbe-lspr = pygbe.lspr:main']},
            #Cython modules with all compilation options
            ext_modules = cythonize([
                Extension("pygbe.tree.multipole",
                          sources=["pygbe/tree/multipole.pyx"],
                          language = "c++",
                          swig_opts=['-c++','-py3'],
                          include_dirs=[numpy.get_include()],
                          extra_compile_args=['-fPIC', '-O3', '-funroll-loops', '-msse3', '-fopenmp'],
                ),
                Extension("pygbe.tree.direct",
                          sources=["pygbe/tree/direct.pyx"],
                          language = "c++",
                          swig_opts=['-c++','-py3'],
                          include_dirs=[numpy.get_include()],
                          extra_compile_args=['-fPIC', '-O3', '-funroll-loops', '-msse3', '-fopenmp'],
                ),
                Extension("pygbe.tree.calculateMultipoles",
                          sources=["pygbe/tree/calculateMultipoles.pyx"],
                          language = "c++",
                          swig_opts=['-c++','-py3'],
                          include_dirs=[numpy.get_include()],
                          extra_compile_args=['-fPIC', '-O3', '-funroll-loops', '-msse3', '-fopenmp'],
                ),
                Extension("pygbe.util.semi_analyticalwrap",
                          sources=["pygbe/util/semi_analyticalwrap.pyx"],
                          language = "c++",
                          swig_opts=['-c++','-py3'],
                          include_dirs=[numpy.get_include()],
                          extra_compile_args=['-fPIC', '-O3', '-funroll-loops', '-msse3', '-fopenmp'],
                ),
                ]),
            )
    setup(**setupkw)

if __name__ == '__main__':
    main()
