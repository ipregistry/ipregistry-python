import setuptools

from ipregistry import __version__

long_description = """
The official Python library for Ipregistry.

Ipregistry is a non-intrusive IP geolocation and threat data lookup solution that retrieves geolocation but also
security information with no explicit permission required from users. All you need is your client's IP address.
"""

setuptools.setup(
    name="ipregistry",
    version=__version__,
    author="Ipregistry",
    author_email="support@ipregistry.co",
    description="Official Python library for Ipregistry",
    long_description=long_description,
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
