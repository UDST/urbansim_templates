from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()
requirements = [item.strip() for item in requirements]

setup(
    name='urbansim_templates',
    version='0.1',
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
        'License :: OSI Approved :: BSD License'
    ],
    packages=find_packages(exclude=['*.tests']),
    install_requires=requirements
)