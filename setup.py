from setuptools import setup, find_packages

setup(
    name='urbansim_templates',
    version='0.1.dev5',
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
    ],
    packages=find_packages(exclude=['*.tests']),
    install_requires=[
        'numpy >= 1.14',
        'orca >= 1.4',
        'pandas >= 0.22',
        'statsmodels >= 0.8',
        'urbansim >= 3.1.1'
    ]
)
