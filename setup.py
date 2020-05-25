import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clear-lambda-storage",
    version="1.0",
    author="",
    author_email="",
    description="Clear Lambda code storage",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/epsagon/clear-lambda-storage",
    py_modules=["clear_lambda_storage"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
    entry_points={
        "console_scripts": [
            "clear_lambda_storage = clear_lambda_storage:main",
        ]
    }
)
