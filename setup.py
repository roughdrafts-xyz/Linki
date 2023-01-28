from setuptools import setup, find_packages

setup(
    name='sigil',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'detools'
    ],
    entry_points={
        'console_scripts': [
            'sigil = sigil.cli:cli',
        ],
    }
)
