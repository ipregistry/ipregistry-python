import setuptools

from ipregistry import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ipregistry",
    version=__version__,
    author="Ipregistry",
    author_email="support@ipregistry.co",
    description="Official Python library for Ipregistry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["cachetools", "requests", "six"],
    url="https://github.com/ipregistry/ipregistry-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Localization"
    ],
)
