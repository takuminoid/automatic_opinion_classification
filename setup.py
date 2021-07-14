import setuptools

with open("README.md", "r") as fh:
    readme = fh.read()

install_requires = [
    "networkx", 
    "mecab-python3", 
    "xlrd==1.2.0", 
    "mojimoji", 
]

setuptools.setup(
    name="automated_opinion_classification", 
    version="0.0.1", 
    install_requires=install_requires, 
    author="Takumi Sato", 
    author_email="takutaku9090@gmail.com", 
    description="This is automatic classifier of opinions using NLP techniques", 
    long_description = readme, 
    long_description_content_type = "text/markdown", 
    url="https://github.com/takuminoid/automatic_opinion_classification", 
    packages = setuptools.find_packages(), 
    classifiers = [
        "Programming Language :: Python :: 3"
    ], 
)