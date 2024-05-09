from django.db import models
from authApi.models import Usuario

class Ubication(models.Model):

    def photo_path(instance, filename): 
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename> 
     return 'ubications/{0}/{1}/{2}'.format(instance.name, 'fotos', filename) 

    name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    manager = models.ForeignKey(Usuario,on_delete=models.SET_NULL, null=True)
    total_becas = models.IntegerField(blank=False, null=False)
    description = models.CharField(max_length=150,blank=True, null=True)
    img = models.ImageField(upload_to=photo_path, blank=True, null=True)
    schedule = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = 'ubicaciones'