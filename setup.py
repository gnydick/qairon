#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = ["argcomplete==2.0.0",
                    "boto3==1.26.5",
                    "botocore==1.29.5",
                    "certifi==2022.9.24",
                    "chardet==5.0.0",
                    "click==8.1.3",
                    "Flask==2.2.2",
                    "idna==3.4",
                    "itsdangerous==2.1.2",
                    "Jinja2==3.1.2",
                    "jmespath==1.0.1",
                    "json-stream==2.1.0",
                    "json-stream-rs-tokenizer==0.4.12",
                    "MarkupSafe==2.1.1",
                    "python-dateutil==2.8.2",
                    "requests==2.28.1",
                    "s3transfer==0.6.0",
                    "six==1.16.0",
                    "urllib3==1.26.12",
                    "Werkzeug==2.2.2",
                    ]
tests_require = ["coverage", "flake8", "pexpect", "wheel", "behave"]
importlib_backport_requires = ["importlib-metadata >= 0.23, < 5"]

setup(
    name='qairon_qcli',
    version='1.2.1',
    url='https://github.com/gnydick/qairon',
    project_urls={},
    license='MIT',
    author='Gabe E. Nydick',
    author_email='gnydick@nydick.net',
    description='Single Source of Truth',
    long_description=open('README.md').read(),
    install_requires=install_requires,
    entry_points = {
        'console_scripts': ['qcli=qairon_qcli.qcli:_main_']
    },
    extras_require={
        ':python_version == "3.9.2"': importlib_backport_requires
    },
    package_dir={"qairon_qcli":"qairon_qcli"},
    packages=['qairon_qcli'],
    scripts=['qairon_qcli/qcli.py'],
    zip_safe=False,
    include_package_data=True,
    platforms=['MacOS X', 'Posix'],
    test_suite='behave',
    classifiers=[]
)
