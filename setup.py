import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gameServerBackend",
    version="0.0.1",
    author="hydrogen602",
    author_email="hydrogen31415@gmail.com",
    description="A framework that interfaces games with websockets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hydrogen602/gameServerBackend",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Framework :: Twisted"
    ],
    python_requires='>=3.7',
)