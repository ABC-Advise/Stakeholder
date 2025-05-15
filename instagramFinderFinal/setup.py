from setuptools import setup, find_packages

setup(
    name="instagram-finder",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "sqlalchemy",
        "python-dotenv",
        "hikerapi",
        "requests"
    ],
) 