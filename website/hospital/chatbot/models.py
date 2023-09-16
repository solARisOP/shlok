from django.db import models

# Create your models here.

class doctor_list(models.Model):
    Id = models.CharField(max_length=3, primary_key=True, null=False)
    name = models.CharField(max_length=122, null=False)

    feilds = (
        (1, "General Practitioner"),
        (2, "Physician"),
        (3, "Cardiologist"),
        (4, "Gastroenterologist"),
        (5, "Dermatologist"),
        (6, "Neurologist"),
        (7, "Orthopedic Surgeon"),
        (8, "Pediatrician"),
        (9, "Gynecologist"),
        (10, "Urologist"),
        (11, "Nephrologist"),
        (12, "Psychiatrist"),
        (13, "Dentist"),
        (14, "Physiotherapist"),
        (15, "Ophthalmologist"),
        (16, "Allergist/Immunologist"),
        (17, "Pulmonologist"),
        (18, "Endocrinologist"),
        (19, "ENT Specialist (Ear, Nose, and Throat)")
    )

    doc_type = models.IntegerField(choices=feilds, null=False)

    gender_fields =(
        (1, "Male"),
        (2, "Female"),
        (3, "Others")
    )
    gender = models.IntegerField(choices=gender_fields, null=False)

    experience = models.IntegerField(null=False)
    fees = models.CharField(max_length=4, null = False)

class doctor_sessions(models.Model):
    doc_Id = models.CharField(max_length=3, null=False)
    session_date = models.DateField(null=False)

    time_fields =(
        (10, "10:00 AM"),
        (14, "02:00 PM"),
        (17, "05:00 PM")
    )
    session_time = models.IntegerField(choices=time_fields, null=False)

    session_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('session_time', 'session_date', 'doc_Id')


class patient_sessions(models.Model):
    doc_Id = models.CharField(max_length=3, null=False)
    session_Id = models.CharField(max_length=7, null=False, primary_key=True)
    pat_Id = models.CharField(max_length=5, null=False,)
    session_date = models.DateField(null=False)
    time_fields =(
        (10, "10:00 AM"),
        (14, "02:00 PM"),
        (17, "05:00 PM")
    )
    session_time = models.IntegerField(choices=time_fields, null=False)

class patient_info(models.Model):
    Id = models.CharField(max_length=5, null=False, primary_key=True)
    name = models.CharField(max_length=122, null=False)
    gender_fields =(
        (1, "Male"),
        (2, "Female"),
        (3, "Others")
    )
    gender = models.IntegerField(choices=gender_fields, null=False)
    DOB = models.DateField(null=False)
    phone = models.CharField(max_length=10, null=False)

class feedback(models.Model):
    details = models.TextField()
    



    

