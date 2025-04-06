from setuptools import setup, find_packages

setup(
    name="smart-j-data-collector",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.0",
        "beautifulsoup4>=4.13.0",
        "flask>=3.0.0",
        "urllib3>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "smart-j-collector=main:main",
        ],
    },
    python_requires=">=3.7",
    author="Mixail_IT",
    description="Data collector for Smart-J website",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
