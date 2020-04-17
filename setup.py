from setuptools import setup, find_packages

setup(
    name='urbansim_templates',
    version='0.2.dev7',
    description='UrbanSim extension for managing model steps',
    author='UrbanSim Inc.',
    author_email='info@urbansim.com',
    url='https://github.com/udst/urbansim_templates',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: BSD License'
    ],
    packages=find_packages(exclude=['*.tests']),
    install_requires=[
        'choicemodels >= 0.2.dev4',
        'numpy >= 1.14',
        'orca >= 1.4',
        'pandas >= 0.23',
        'patsy >= 0.4',
        'statsmodels >= 0.8, <0.11; python_version <"3.6"',
        'statsmodels >= 0.8; python_version >="3.6"',
        'urbansim >= 3.1'
    ]
)