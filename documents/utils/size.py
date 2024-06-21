import math

def convert_size(size_bytes):
    """
    Convert bytes to human readable size

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Human readable size
    """
    if size_bytes == 0:
        return "0 B"
    
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"