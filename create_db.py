import os
import shutil
from main import db


if os.path.exists('data.db'):
    os.remove('data.db')
if os.path.exists('static/files'):
    shutil.rmtree('static/files')
os.mkdir('static/files')
db.create_all()
