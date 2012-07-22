from setuptools import setup, Extension
import os
repo_path = "%s/app-root/repo/" % os.environ['HOME']

setup(name='gdbflee',
      version='0.1',
      description='A simple web app for helping your data flee a Personal Geodatabase.',
      author='Michael Weisman',
      author_email='mweisman@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['Flask>=0.7.2']
     )

setup (name='fgdb',
      version='0.1',
      description='Light wrapper around GDAL/FileGDB for freeing data.',
      ext_modules=[Extension(
      'fgdb',
       sources=[repo_path + '/fgdb/src/fgdb.c'],
       include_dirs=[repo_path + '/libs/include'],
       library_dirs=[repo_path + '/libs/lib'],
       libraries=['gdal'])
       ]
     )
