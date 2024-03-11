import logging

# To be developed
def create_logger(lof_path:str = ".logs/access.log"):
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(lof_path)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
