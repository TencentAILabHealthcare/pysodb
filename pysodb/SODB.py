import os
import requests
import numpy as np
import pandas as pd
import scanpy as sc
from tqdm import tqdm
import shutil
from urllib.request import urlopen, Request
import tempfile


def download_url_to_file(url, dst, hash_prefix=None, progress=True):
    r"""Download object at the given URL to a local path.
        borrow from torchvision
    Args:
        url (string): URL of the object to download
        dst (string): Full path where object will be saved, e.g. `/tmp/temporary_file`
        hash_prefix (string, optional): If not None, the SHA256 downloaded file should start with `hash_prefix`.
            Default: None
        progress (bool, optional): whether or not to display a progress bar to stderr
            Default: True
    """
    file_size = None
    # We use a different API for python2 since urllib(2) doesn't recognize the CA
    # certificates in older Python
    req = Request(url, headers={"User-Agent": "torch.hub"})
    u = urlopen(req)
    meta = u.info()
    if hasattr(meta, 'getheaders'):
        content_length = meta.getheaders("Content-Length")
    else:
        content_length = meta.get_all("Content-Length")
    if content_length is not None and len(content_length) > 0:
        file_size = int(content_length[0])

    # We deliberately save it in a temp file and move it after
    # download is complete. This prevents a local working checkpoint
    # being overridden by a broken download.
    dst = os.path.expanduser(dst)
    dst_dir = os.path.dirname(dst)
    f = tempfile.NamedTemporaryFile(delete=False, dir=dst_dir)

    try:
        if hash_prefix is not None:
            sha256 = hashlib.sha256()
        with tqdm(total=file_size, disable=not progress,
                  unit='B', unit_scale=True, unit_divisor=1024) as pbar:
            while True:
                buffer = u.read(8192)
                if len(buffer) == 0:
                    break
                f.write(buffer)
                if hash_prefix is not None:
                    sha256.update(buffer)
                pbar.update(len(buffer))

        f.close()
        if hash_prefix is not None:
            digest = sha256.hexdigest()
            if digest[:len(hash_prefix)] != hash_prefix:
                raise RuntimeError('invalid hash value (expected "{}", got "{}")'
                                   .format(hash_prefix, digest))
        shutil.move(f.name, dst)
    finally:
        f.close()
        if os.path.exists(f.name):
            os.remove(f.name)


class SODB:
    def __init__(self, storage_path=None, server_address="https://gene.ai.tencent.com/SpatialOmics/api/pysodb"):
        """
            storage_path: str, path to store data. default: the package installation directory
            server_address: str, URL for server

            usage:
                sodb = pysodb.SODB()
                sodb.list_dataset_by_category("Spatial Transcriptomics")
                a = sodb.load_dataset("MALDI_lung")
                b = sodb.load_experiment("MALDI_lung", "nanostring_fov17_sampledata")
        """
        self.server_address = server_address
        if storage_path is None:
            self.storage_path = self.__get_cache_path()
        self.data = None
        self.__get_info()
    
    def __get_info(self, ):
        """load basic info from the server"""
        res = requests.get(self.server_address + "/info")
        if res.status_code == 200:
            res_json = res.json()
            if res_json["code"] == 0 and len(res_json["data"]) > 0:
                data = np.array(res_json["data"])
                self.data = pd.DataFrame({
                    "biotech_category": data[:, 0],
                    "dataset_name": data[:, 1],
                    "experiment_name": data[:, 2]
                })
            else:
                raise Exception("Failed to load data from the server")
        else:
            raise Exception("Failed to connect to the server")
            
    def __get_cache_path(self, ):
        return os.path.join(os.path.split(os.path.realpath(__file__))[0], "cache")

    def list_dataset(self, ):
        """
           return: list of datasets (short name): [str, ...]
        """
        return list(set(self.data.loc[:, "dataset_name"].values.tolist()))

    def list_dataset_by_category(self, biotech_category):
        """
            args: biotech category: str, Spatial Transcriptomics/Spatial Proteomics/Spatial Metabolomics/Spatial Genomics/Spatial MultiOmics
            return: list of datasets (short name): [str, ...]
        """
        biotech_category_list = set(self.data.loc[:, "biotech_category"].values.tolist())
        assert biotech_category in biotech_category_list, 'Unkown biotech category: {}, Available categories are "Spatial Transcriptomics", "Spatial Proteomics", "Spatial Metabolomics", "Spatial Genomics", "Spatial MultiOmics". '.format(biotech_category)
        return list(set(self.data[self.data.biotech_category == biotech_category].loc[:, "dataset_name"].values.tolist()))

    def list_experiment_by_dataset(self, dataset_name):
        """
            args: dataset_name: str, eg: liu2020high, names can get by funcs list_dataset / list_dataset_by_category
            return: list of experiments in dataset: [str, ...]
        """
        if len(self.data[self.data.dataset_name == dataset_name]) <= 0:
            raise Exception("dataset[{}] does not exist. You could get available datasets by calling the function list_dataset.".format(dataset_name))
        return self.data[(self.data.dataset_name == dataset_name)].loc[:, "experiment_name"].values.tolist()
    
    def load_dataset(self, dataset_name):
        """
            args:
                dataset_name: str, eg: liu2020high, names can get by funcs list_dataset / list_dataset_by_category
            return:
                output: dict[experiment_name] = the Anndata object
        """
        if len(self.data[self.data.dataset_name == dataset_name]) <= 0:
            raise Exception("dataset[{}] does not exist. You could get available datasets by calling the function list_dataset.".format(dataset_name))
        experiment_name_list = self.data[self.data.dataset_name == dataset_name].loc[:, "experiment_name"].values.tolist()
        return {en : self.load_experiment(dataset_name, en) for en in experiment_name_list}


    def load_experiment(self, dataset_name, experiment_name):
        """
            args: 
                dataset_name: str, eg: chen2021dissecting
                experiment_name: str, eg: GSM4202309_0719aL_protein
            return :
                the Anndata object read by scanpy
        """
        if len(self.data[self.data.dataset_name == dataset_name]) <= 0:
            raise Exception("dataset[{}] does not exist. You could get available datasets by calling the function list_dataset.".format(dataset_name))
        if len(self.data[(self.data.dataset_name == dataset_name) & (self.data.experiment_name == experiment_name)]) <= 0:
            raise Exception("experiment[{}] does not exist in dataset[{}]. You could get available experiments in dataset[{}] by calling the function list_experiment_by_dataset.".format(experiment_name, dataset_name, dataset_name))
        tmp_storage_path = os.path.join(self.storage_path, dataset_name, experiment_name+".h5ad")
        if not os.path.exists(tmp_storage_path):
            os.makedirs(os.path.join(self.storage_path, dataset_name), exist_ok=True)
            # download
            print("download experiment[{}] in dataset[{}]".format(experiment_name, dataset_name))
            download_url_to_file(self.server_address + "/download/{}/{}".format(dataset_name, experiment_name), tmp_storage_path)
        try:
            print("load experiment[{}] in dataset[{}]".format(experiment_name, dataset_name))
            data = sc.read_h5ad(tmp_storage_path)
        except: 
            print("False to load experiment[{}] in dataset[{}], please try again later.".format(experiment_name, dataset_name))
            os.remove(tmp_storage_path)
            data = None
        return data
