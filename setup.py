from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

def _post_install(setup):
    def _unzip():
        from postal_to_geocode import uncompress_db
        print('uncompressing db file')
        uncompress_db()
    _unzip()
    return setup

_post_install(
    setup(
        name='Postal To Geocode',
        version='0.01b',
        packages=['postal_to_geocode',],
        license='Creative Commons Attribution-Noncommercial-Share Alike license',
        long_description=open('README.txt').read(),
        include_package_data=True,
        zip_safe=False,
    ))
