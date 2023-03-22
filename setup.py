import setuptools

setuptools.setup(
    name="pysodb", # Replace with your own username
    version="1.0.0",
    author="wentao pan",
    author_email="panwentao1301@gmail.com",
    description="SODB interface for python",
    url="https://gene.ai.tencent.com/SpatialOmics/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires = [
    'scanpy',
    'pandas',
    'numpy',
    'requests',
    'urllib3>=1.26.12',
    'tqdm',
    'anndata'
    ] 
)
