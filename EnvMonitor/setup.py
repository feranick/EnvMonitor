from setuptools import setup, find_packages

setup(
    name='EnvMonitor',
    packages=find_packages(),
    install_requires=['pymongo'],
    entry_points={'console_scripts' : ['EnvMonitor=EnvMonitor:EnvMonitor']},
    py_modules=['EnvMonitor'],
    version='20190303ac',
    description='Environmental tracking monitor with submission to mongo',
    long_description= """ Environmental tracking monitor with submission to mongo """,
    author_email='ferralis@mit.edu',
    url='https://github.com/feranick/EnvMonitor',
    download_url='https://github.com/feranick/EnvMonitor/archive/master.zip',
    keywords=['Data', 'Environment', 'tracking', 'automation',],
    license='GPLv3',
    platforms='any',
    classifiers=[
     'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
     'Development Status :: 4 - Beta',
     'Programming Language :: Python :: Only',
     'Programming Language :: Python :: 3',
     'Programming Language :: Python :: 3.5',
     'Programming Language :: Python :: 3.6',
     'Intended Audience :: Science/Research',
     'Topic :: Scientific/Engineering :: Chemistry',
     'Topic :: Scientific/Engineering :: Physics',
     ],
)
