import pysodb

sodb = pysodb.SODB() # Initialization
dataset_list = sodb.list_dataset() # Get the list of datasets
dataset_list = sodb.list_dataset_by_category("Spatial Transcriptomics") # Get the list of datasets with specific category. categories ["Spatial Transcriptomics", "Spatial Proteomics", "Spatial Metabolomics", "Spatial Genomics", "Spatial MultiOmics"]
print(sodb.list_experiment_by_dataset("yuan2021seam"))
# dataset = sodb.load_dataset("yuan2021seam ") # Load a specific dataset 
data = sodb.load_experiment("parigi2022the", "GSM5213483_V19S23-097_A1_S1 ") # Load a specific experiment 
# print(dataset.keys())