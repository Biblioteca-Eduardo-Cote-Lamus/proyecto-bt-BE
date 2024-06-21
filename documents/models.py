from django.db import models
from .utils import convert_size
# Create your models here.

class Document(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='documents')
    date_created = models.DateTimeField(auto_now_add=True)
    size = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):  
        self.size = convert_size(self.file.size)
        super(Document, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'documentos'

    def __str__(self):
        return self.name