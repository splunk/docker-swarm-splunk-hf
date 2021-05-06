from setuptools import setup, find_packages

setup(
    name="metricscheck",
    packages=find_packages(),
    install_requires=[
        "file-read-backwards",
    ],
    include_package_data=True,
)
