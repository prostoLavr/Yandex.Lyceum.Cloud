import tarfile
import os
from typing import List
from . import config


class Compressor:
    def compress(file_name: str):
        archive_name = file_name.replace('temp_', '') + '.tar.gz'
        with tarfile.open(os.path.join(config.files_path, archive_name), "w:gz") as tar:
            tar.add(os.path.join(config.files_path, file_name))
    
    def get_files_names(archive_name) -> List[str]:
        with tarfile.open(os.path.join(config.files_path, archive_name), 'r:gz') as tar:
            return [file.name for file in tar]
        
    def get_file(file_name):
        """
        :return: file as io.BufferedReader
        """
        archive_name = file_name + '.tar.gz'
        with tarfile.open(os.path.join(config.files_path, archive_name), 'r:gz') as tar:
            return tar.extractfile(file_name)
    
    def delete_file(file_name):
        os.remove(os.path.join(config.files_path, file_name + '.tar.gz'))