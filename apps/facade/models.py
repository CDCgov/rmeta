from django.db import models
from ..report_metadata.models import HealthDataType, ProgramAreaType
from oauth2_provider.models import Application
import uuid

class DataStream(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    description = models.TextField()
    allowable_payload_types = models.ManyToManyField(HealthDataType, 
                                        blank=True,
                                        related_name='allowable_payload_types')
    reviewers = models.ManyToManyField('auth.Group', related_name ='reviewers',
                                        blank=True)
    program_area = models.ManyToManyField(ProgramAreaType, blank=True, 
                                        related_name='program_area')
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Origin(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    application = models.ForeignKey(Application, on_delete=models.CASCADE,
                                    null=True, blank=True)
    data_streams = models.ManyToManyField(DataStream,  blank=True,
                                        related_name='data_streams')

    description = models.TextField()
    url = models.URLField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
    
    def save(self, *args, **kwargs):
        self.url = f"/facade/orginator/{self.code}"
        super().save(*args, **kwargs)

class Submission(models.Model):
    tcn = models.CharField(max_length=100, blank=True, verbose_name="Transaction Control Number")
    tcr = models.CharField(max_length=100, blank=True, verbose_name="Transaction Control Reference")
    dai_tcn = models.CharField(max_length=100, blank=True, verbose_name="Destination Transaction Control Number")
    ori  = models.ForeignKey(Origin, on_delete=models.CASCADE, verbose_name="Originating Agency Identifier",
                             related_name='originating_agency', blank=True, null=True)
    cri_1 = models.CharField(max_length=100, blank=True, verbose_name="Contributing Identifier 1")
    cri_2 = models.CharField(max_length=100, blank=True, verbose_name="Contributing Identifier 2") 
    cri_3 = models.CharField(max_length=100, blank=True, verbose_name="Contributing Identifier 3") 
    cri_4 = models.CharField(max_length=100, blank=True, verbose_name="Contributing Identifier 4")
    cri_5 = models.CharField(max_length=100, blank=True, verbose_name="Contributing Identifier 5")
    dai = models.CharField(max_length=100, blank=True, default="CDC-1CDP-1",verbose_name="Destination Agency Identifier")
    status_url = models.URLField(blank=True)
    status = models.CharField(max_length=100, choices=[('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('ACCEPTED', 'ACCEPTED')])
    multiple_entries = models.BooleanField(default=False, blank=True)
    payload_type = models.ForeignKey(HealthDataType, on_delete=models.CASCADE)
    payload = models.TextField(blank=True)
    payload_file = models.FileField(upload_to='uploads/', blank=True)
    response_json = models.TextField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.tcn}-{self.ori}"
    def save(self, *args, **kwargs):
        if not self.tcn or not self.dai_tcn:
            self.dai_tcn = str(uuid.uuid4())

        
        self.status_url = f"{self.status_url}/{self.tcn}"
        super().save(*args, **kwargs)


class SubmissionHistory(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=[('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('ACCEPTED', 'ACCEPTED')])
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.submission}-{self.status}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.submission.status = self.status
        self.submission.response_json = self.response_json
        self.submission.save()

