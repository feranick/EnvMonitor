from setuptools import setup, find_packages

setup(
    name='EnvMonitor',
    packages=find_packages(),
    install_requires=['pymongo'],
    entry_points={'console_scripts' : ['EnvMonitor=EnvMonitor:EnvMonitor',
        'EnvMonitorNest=EnvMonitorNest:EnvMonitorNest','GetEnvData=GetEnvData:GetEnvData',
        'GetEnvNest=GetEnvNest:GetEnvNest', 'EnvMonitorLite=EnvMonitorLite:EnvMonitorLite',]},
    py_modules=['EnvMonitor','EnvMonitorNest','EnvMonitorLite','GetEnvData','libEnvMonitor','PMsensor','Sensors',
        'GetEnvNest','GNestAccess'],
    scripts=['EnvMonitor_launcher.sh', 'EnvMonitorNest_launcher.sh', 'EnvMonitorLite_launcher.sh'],
    version='20210505a',
    description='Environmental tracking monitor with submission to mongo or CSV',
    long_description= """ Environmental tracking monitor with submission to mongo or CSV """,
    author_email='ferralis@mit.edu',
    url='https://github.com/feranick/EnvMonitor',
    download_url='https://github.com/feranick/EnvMonitor/archive/master.zip',
    keywords=['Data', 'Environment', 'tracking', 'automation','eCO2','Nest'],
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
     'Programming Language :: Python :: 3.10',
     'Intended Audience :: Science/Research',
     'Topic :: Scientific/Engineering :: Chemistry',
     'Topic :: Scientific/Engineering :: Physics',
     ],
)
