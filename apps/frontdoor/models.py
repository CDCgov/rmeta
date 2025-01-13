from django.db import models
from ..report_metadata.models import HealthDataType, ProgramAreaType
from oauth2_provider.models import Application
import uuid
from django.conf import settings

__author__ = "Alan Viars"

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
    code = models.CharField(max_length=100, db_index=True)
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
    
    @property
    def ori(self):
        return self.code

    def save(self, *args, **kwargs):
        self.url = f"{settings.HOSTNAME_URL}/frontdoor/ori/{self.code}"
        super().save(*args, **kwargs)

class Transaction(models.Model):
    tcn = models.CharField(max_length=64, blank=True, verbose_name="Transaction Control Number", 
                           unique=True, db_index=True)
    tcr = models.CharField(max_length=64, blank=True, verbose_name="Transaction Control Reference",
                           db_index=True)
    dai_tcn = models.CharField(max_length=100, blank=True, verbose_name="Destination Transaction Control Number")
    ori  = models.ForeignKey(Origin, on_delete=models.CASCADE, verbose_name="Originating Agency Identifier",
                             related_name='originating_agency', blank=True, null=True, db_index=True)
    cri_1 = models.CharField(max_length=100, blank=True, verbose_name="Contributing Agency Identifier 1")
    cri_2 = models.CharField(max_length=100, blank=True, verbose_name="Contributing Agency Identifier 2") 
    cri_3 = models.CharField(max_length=100, blank=True, verbose_name="Contributing Agency Identifier 3") 
    cri_4 = models.CharField(max_length=100, blank=True, verbose_name="Contributing Agency Identifier 4")
    cri_5 = models.CharField(max_length=100, blank=True, verbose_name="Contributing Agency Identifier 5")
    dai = models.CharField(max_length=100, blank=True, default="CDC-1CDP-1",verbose_name="Destination Agency Identifier")
    status_url = models.URLField(blank=True, default=f'{settings.HOSTNAME_URL}/frontdoor/transaction/status/')
    status = models.CharField(max_length=100, blank=True, default="PENDING", choices=[('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('ACCEPTED', 'ACCEPTED')])
    multiple_entries = models.BooleanField(default=False, blank=True)
    payload_type = models.ForeignKey(HealthDataType, on_delete=models.CASCADE)
    payload = models.TextField(blank=True)
    payload_file = models.FileField(upload_to='uploads/', blank=True)
    response_json = models.TextField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.tcn}-{self.ori}"
    
    @property
    def response_tcn(self):
        return self.dai_tcn

    def save(self, *args, **kwargs):
        if not self.tcn or not self.dai_tcn:
            self.dai_tcn = str(uuid.uuid4())        
        self.status_url = f"{self.status_url}/{self.tcn}"
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

class TransactionHistory(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=[('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('ACCEPTED', 'ACCEPTED')])
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    class Meta:
        verbose_name = "Transaction History"
        verbose_name_plural = "Transaction Histories"

    def __str__(self):
        return f"{self.submission}-{self.status}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.transaction.status = self.status
        self.transaction.response_json = self.response_json
        self.transaction.save()

