import os

def create_dev_and_prod_directories():
    dev_dir = "../dev"
    prod_dir = "../prod"
    if not os.path.isdir(dev_dir):
        os.makedirs(dev_dir)
    if not os.path.isdir(prod_dir):
        os.makedirs(prod_dir)
