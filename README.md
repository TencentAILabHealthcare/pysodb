# pysodb
## Introduction
pysodb is a python package that provides the interface to access the data in [SODB](https://gene.ai.tencent.com/SpatialOmics/).

## Installation
1. Create a conda environment and activate it.
```
conda create --name pysodb python=3.8 -y
conda activate pysodb
```
2. Clone the source code.
```
git clone https://github.com/TencentAILabHealthcare/pysodb.git
```
2. Install pysodb as a dependency or third-party package with pip:
```
cd pysodb
python setup.py install
```

## Usage
```
import pysodb

sodb = pysodb.SODB() # Initialization

dataset_list = sodb.list_dataset() # Get the list of datasets

dataset_list = sodb.list_dataset_by_category() # Get the list of datasets with specific category. categories ["Spatial Transcriptomics", "Spatial Proteomics", "Spatial Metabolomics", "Spatial Genomics", "Spatial MultiOmics"]

data = sodb.load_experiment("yuan2021seam", "NCTC1469withIdU_Hepa1-6_pixel") # Load a specific experiment 

dataset = sodb.load_dataset("yuan2021seam") # Load a specific dataset
```
