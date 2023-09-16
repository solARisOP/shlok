from django.contrib import admin
from chatbot.models import doctor_list, doctor_sessions, patient_sessions, patient_info, feedback
# Register your models here.

admin.site.register(doctor_list)
admin.site.register(doctor_sessions)
admin.site.register(patient_sessions)
admin.site.register(patient_info)
admin.site.register(feedback)

