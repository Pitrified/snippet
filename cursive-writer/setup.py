import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cursive_writer",
    version="0.0.1",
    author="Pitrified",
    author_email="pitrified.git@gmail.com",
    description="Tools to draw and compose cursive letters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pitrified/snippet/cursive-writer",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["Pillow"],
)
