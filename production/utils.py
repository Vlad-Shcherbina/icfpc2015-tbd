import os


_project_root = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def get_project_root():
    return _project_root


def get_data_dir():
    return os.path.join(_project_root, 'data')
