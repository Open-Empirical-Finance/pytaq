import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytaq",
    version="0.0.1",
    author="Vincent Grégoire",
    author_email="vincent.gregoire@gmail.com",
    description="A package to parse and process TAQ data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vgreg/pytaq",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "src"},
    # packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)