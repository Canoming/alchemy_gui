from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
   name='alchemy_gui',
   version='0.2',
   description='A gui for tuining hyperparameters of python scripts',
   license="MIT",
   long_description=long_description,
   author='Ximing Wang',
   author_email='canoming.sktt@gmail.com',
   packages=['alchemy_gui'],  #same as name
   install_requires=[
       'pyHtmlGui',
   ], #external packages as dependencies
   entry_points = {
       'console_scripts': [
              'alchemygui = alchemy_gui.main:main',
         ],
   },
)