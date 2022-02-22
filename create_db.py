import os
from main import db


os.system('rm data.db')
os.system('rm -rf static/files')
os.system('mkdir static/files')
db.create_all()
