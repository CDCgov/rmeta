from django.db import models

# Create your models here.

class BirthCertificate(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=10)
    registration_date = models.DateField(auto_now_add=True)
    registration_number = models.CharField(max_length=100, unique=True)
    # Add more fields as needed

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.registration_number}"
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    registration_date = models.DateField(auto_now_add=True)
    registration_number = models.CharField(max_length=100, unique=True)
    # Add more fields as needed

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.registration_number}"

class DeathCertificate(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_death = models.DateField()
    place_of_death = models.CharField(max_length=100)
    cause_of_death = models.CharField(max_length=100)
    informant_name = models.CharField(max_length=100)
    informant_relationship = models.CharField(max_length=100)
    registration_date = models.DateField(auto_now_add=True)
    registration_number = models.CharField(max_length=100, unique=True)
    # Add more fields as needed

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.registration_number}"