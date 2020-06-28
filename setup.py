from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='cf_submit',
    version='1.3.5',
    scripts=['cf'],
    author='Nasreddine Bac Ali',
    author_email='nasreddine.bacali95@gmail.com',
    description='Submit Codeforces codes via terminal and other coll stuff',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bacali95/cf_submit',
    packages=find_packages(),
    package_data={
        'cf_submit': [
            'bin/cf_checker',
            'bash_completion/cf'
        ]
    },
    install_requires=[
        'lxml',
        'robobrowser',
        'prettytable',
        'javalang',
        'requests',
        'Werkzeug>=0.16,<1.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
