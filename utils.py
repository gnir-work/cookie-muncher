import os

OUTPUT_FIXTURE = 'csv'
LOG_FIXTURE = 'log'


def check_directory_exists(path):
    """
    Checks if the path exists, if it doesn't creates it.
    :param path: The path to be checked.
    """
    if not os.path.exists(path):
        os.makedirs(path)
