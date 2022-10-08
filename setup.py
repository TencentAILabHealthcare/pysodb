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
    'scanpy>=1.9.1',
    'pandas>=1.5.0',
    'numpy>=1.23.3',
    'requests>=2.28.1',
    'urllib3>=1.26.12',
    'tqdm>=4.64.1'
    ] 
)