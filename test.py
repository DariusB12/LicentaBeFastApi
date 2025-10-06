from typing import Dict

import os
import tensorflow as tf
import torch

DATABASE_URL = os.getenv("DATABASE_URL")

if __name__ == "__main__":
    # tf.config.list_physical_devices('GPU')
    print(torch.cuda.is_available())
    # print(DATABASE_URL)
    # clients_connections: Dict[int, int] = {}
    #
    # clients_connections.pop(1,None)
