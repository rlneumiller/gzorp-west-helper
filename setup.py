from setuptools import setup, find_packages

setup(
    name="west_helper",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pyyaml>=6.0.1",
    ],
    author="Arrel",
    author_email="rlneumiller@gmail.com",
    description="A zephyr west helper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rlneumiller/west_helper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'west_helper=west_helper.main:main',
        ],
    },
    license="Apache License 2.0",
)
