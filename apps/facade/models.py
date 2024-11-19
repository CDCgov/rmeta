from django.db import models
from ..report_metadata.models import HealthDataType
from oauth2_provider.models import Application
class DataStream(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    submitters = models.ManyToManyField('auth.Group', related_name='submitters')
    reviewers = models.ManyToManyField('auth.Group', related_name ='reviewers')
    url = models.URLField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.url}"

class Incomming(models.Model):
    data_stream = models.ForeignKey(DataStream, on_delete=models.CASCADE)
    origin_agency_identifier = models.CharField(max_length=100)
    intermediate_agency_identifier = models.CharField(max_length=100, blank=True) 
    destination_agency_identifier = models.CharField(max_length=100, default="CDC-1CDP-1")
    url = models.URLField(blank=True)
    status = models.CharField(max_length=100, choices=[('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('ACCEPTED', 'ACCEPTED')])
    payload_type = models.ForeignKey(HealthDataType, on_delete=models.CASCADE)
    payload = models.TextField()
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

