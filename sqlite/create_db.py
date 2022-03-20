import os
import shutil
from app.db_manager import db_obj

files_path = '../app/static/files'
if os.path.exists('data.db'):
    os.remove('data.db')
if os.path.exists(files_path):
    shutil.rmtree(files_path)
os.mkdir(files_path)
db_obj.create_all()
