from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

class PostDevelopCommand(develop):
    def run(self):
        from postal_to_geocode import uncompress_db
        uncompress_db()
        develop.run(self)

class PostInstallCommand(install):
    def run(self):
        from postal_to_geocode import uncompress_db
        uncompress_db()
        install.run(self)


setup(
    name='Postal To Geocode',
    version='0.01b',
    packages=['postal_to_geocode',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    install_requires=['unicodecsv'],
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
)
