from __future__ import absolute_import
import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('codegen_models/_version.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='codegen-models',
    description='Generate WXapp Model (MVC) code from Swagger docs.',
    version=version,
    author='legenove',
    author_email='396410414@qq.com',
    packages=['codegen_models'],
    package_data={'templates': ['codegen_models/templates/*']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'codegen_models=codegen_models:generate'
        ]
    },
    install_requires=['PyYAML', 'click', 'jinja2', 'dpath', 'six'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
)
