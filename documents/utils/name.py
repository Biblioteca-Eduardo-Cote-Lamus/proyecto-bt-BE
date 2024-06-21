
def get_name(*,name, originalname):
    ext = originalname.split('.')[-1]
    return '{}.{}'.format(name, ext)