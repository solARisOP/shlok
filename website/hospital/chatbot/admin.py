from django.contrib import admin
from chatbot.models import doctor_list, doctor_session, patient_session, patient_info, feedback
# Register your models here.

admin.site.register(doctor_list)
admin.site.register(doctor_session)
admin.site.register(patient_session)
admin.site.register(patient_info)
admin.site.register(feedback)

