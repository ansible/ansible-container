from setuptools import setup
import harbormaster

setup(
    name='harbormaster',
    version=harbormaster.__version__,
    packages=['harbormaster', 'harbormaster.shipit'],
    include_package_data=True,
    url='https://github.com/j00bar/ansibleharbormaster',
    license='LGPLv3 (See LICENSE file for terms)',
    author='Joshua "jag" Ginsberg and others (See AUTHORS file for contributors)',
    author_email='jag@flowtheory.net',
    description=('Harbormaster empowers you to orchestrate, build, run, and ship '
                 'Docker images built from Ansible playbooks.'),
    entry_points={
        'console_scripts': ['harbormaster = harbormaster.cli:commandline']
    }
)
