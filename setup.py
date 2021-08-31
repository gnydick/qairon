#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = ["argcomplete==1.12.3",
                    "boto3==1.17.88",
                    "botocore==1.20.88",
                    "certifi==2021.5.30",
                    "chardet==4.0.0",
                    "click==8.0.1",
                    "Flask==2.0.1",
                    "idna==2.10",
                    "itsdangerous==2.0.1",
                    "Jinja2==3.0.1",
                    "jmespath==0.10.0",
                    "MarkupSafe==2.0.1",
                    "python-dateutil==2.8.1",
                    "requests==2.25.1",
                    "s3transfer==0.4.2",
                    "six==1.16.0",
                    "urllib3==1.26.5",
                    "Werkzeug==2.0.1",
                    ]
tests_require = ["coverage", "flake8", "pexpect", "wheel", "behave"]
importlib_backport_requires = ["importlib-metadata >= 0.23, < 5"]

setup(
    name='qairon-qcli',
    version='0.0.13',
    url='https://github.com/gnydick/qairon',
    project_urls={},
    license='MIT',
    author='Gabe E. Nydick',
    author_email='gnydick@nydick.net',
    description='Single Source of Truth',
    long_description=open('README.md').read(),
    install_requires=install_requires,
    extras_require={
        ':python_version == "3.9.2"': importlib_backport_requires
    },
    packages=find_packages(exclude=("features", "features.*", "models", "views", "views.*")),
    scripts=['qcli'],
    zip_safe=False,
    include_package_data=True,
    platforms=['MacOS X', 'Posix'],
    test_suite='behave',
    classifiers=[]
)
