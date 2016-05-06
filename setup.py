from setuptools import setup

setup(
    name='harbormaster',
    version='0.1',
    packages=['harbormaster'],
    include_package_data=True,
    url='',
    license='Not licensed for distribution',
    author='Joshua "jag" Ginsberg',
    author_email='jag@redhat.com',
    description='',
    entry_points={
        'console_scripts': ['harbormaster = harbormaster.cli:commandline']
    }
)
