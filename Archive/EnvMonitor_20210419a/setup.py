from setuptools import setup, find_packages

setup(
    name='EnvMonitor',
    packages=find_packages(),
    install_requires=['pymongo'],
    entry_points={'console_scripts' : ['EnvMonitor=EnvMonitor:EnvMonitor','GetEnvData=GetEnvData:GetEnvData',
        'EnvMonNest=EnvMonNest:EnvMonNest', 'EnvMonitorLite=EnvMonitorLite:EnvMonitorLite']},
    py_modules=['EnvMonitor','EnvMonitorLite','GetEnvData','libEnvMonitor','PMsensor','BMP180sensors','Tsensors',
        'Gassensors','EnvMonNest','GNestAccess'],
    scripts=['EnvMonitor_launcher.sh', 'EnvMonitorLite_launcher.sh', 'EnvMonNest_launcher.sh'],
    version='20210419a',
    description='Environmental tracking monitor with submission to mongo or CSV',
    long_description= """ Environmental tracking monitor with submission to mongo or CSV """,
    author_email='ferralis@mit.edu',
    url='https://github.com/feranick/EnvMonitor',
    download_url='https://github.com/feranick/EnvMonitor/archive/master.zip',
    keywords=['Data', 'Environment', 'tracking', 'automation','eCO2'],
    license='GPLv3',
    platforms='any',
    classifiers=[
     'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
     'Programming Language :: Python :: Only',
     'Programming Language :: Python :: 3',
     'Programming Language :: Python :: 3.5',
     'Programming Language :: Python :: 3.6',
     'Programming Language :: Python :: 3.7',
     'Programming Language :: Python :: 3.8',
     'Programming Language :: Python :: 3.9',
     'Intended Audience :: Science/Research',
     'Topic :: Scientific/Engineering :: Chemistry',
     'Topic :: Scientific/Engineering :: Physics',
     ],
)
