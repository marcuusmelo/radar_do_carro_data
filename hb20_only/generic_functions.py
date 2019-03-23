import os

def check_if_folder_exists_than_crete(folder_path):
    """ Check if folder already exists than create if not """
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)


def check_if_file_exists(file_path):
    """ Check if file already exists """
    if os.path.exists(file_path):
        return True
    else:
        return False
