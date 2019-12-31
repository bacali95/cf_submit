from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='cf_submit',
    version='1.2.2',
    scripts=['cf'],
    author='Nasreddine Bac Ali',
    author_email='nasreddine.bacali95@gmail.com',
    description='Submit Codeforces codes via terminal and other coll stuff',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bacali95/cf_submit',
    packages=['cf_submit'],
    package_data={
        'cf_submit': [
            'cf_checker',
            'auto_complete_cf',
            'hack_prob.sh'
        ]
    },
    install_requires=[
        'lxml',
        'robobrowser',
        'prettytable',
        'javalang'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
