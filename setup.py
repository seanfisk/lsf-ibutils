import os
import sys

from setuptools import setup

sys.path.append('.')
from lsf_ibutils import metadata


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


# define install_requires for specific Python versions
python_version_specific_requires = []

# as of Python >= 2.7 and >= 3.2, the argparse module is maintained within
# the Python standard library, otherwise we install it as a separate package
if sys.version_info < (2, 7) or (3, 0) <= sys.version_info < (3, 3):
    python_version_specific_requires.append('argparse')


# See here for more options:
# <http://pythonhosted.org/setuptools/setuptools.html>
setup_dict = dict(
    name=metadata.package,
    version=metadata.version,
    author=metadata.authors[0],
    author_email=metadata.emails[0],
    maintainer=metadata.authors[0],
    maintainer_email=metadata.emails[0],
    url=metadata.url,
    description=metadata.description,
    long_description=read('README.rst'),
    download_url=metadata.url,
    # Find a list of classifiers here:
    # <http://pypi.python.org/pypi?%3Aaction=list_classifiers>
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: System :: Distributed Computing',
        'Topic :: Utilities',
    ],
    packages=['lsf_ibutils', 'lsf_ibutils.ibsub'],
    install_requires=[
        'pinject>=0.10',
        'psutil>=1.0.1',
    ] + python_version_specific_requires,
    zip_safe=False,  # don't use eggs
    entry_points={
        'console_scripts': [
            'ibsub = lsf_ibutils.ibsub.main:entry_point'
        ],
    }
)


def main():
    setup(**setup_dict)


if __name__ == '__main__':
    main()
