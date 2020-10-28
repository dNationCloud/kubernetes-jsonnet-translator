from setuptools import setup, find_packages


install_requires = [
    "jsonnet==0.16.*",
    "kubernetes==12.0.*",
    "patool==1.12",
    "urllib3==1.25.*",
]


setup(
    name="jsonnet_k8s_translator",
    description="Generates json resources from jsonnet resources",
    author="Dnation",
    author_email="david.suba@dnation.tech",
    version="1.0.0",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=["black", "flake8"],
)
