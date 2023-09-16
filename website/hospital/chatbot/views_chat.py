# Create your views here.
from django.http import JsonResponse
from chatbot import symptom_doc_matcher
from chatbot import pred
import json
import random
from django.db import connection
from chatbot.models import doctor_list, doctor_sessions, patient_sessions, patient_info
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist

file_path = "chatbot/responses.json"
with open(file_path, 'r') as json_file:
    response = json.load(json_file)

default_template = '''\n
"Booking your new appointment" \n
"Cancel your appointment" \n
"Reschedule your appointment" \n
"details/status of the appointment you have booked" \n
"Providing a feedback about your last visit" \n
Please let me know about your request.
 '''

doct_types = '''1. General Practitioner (GP)\n
    2. Physician\n
    3. Cardiologist\n
    4. Gastroenterologist\n
    5. Dermatologist\n
    6. Neurologist\n
    7. Orthopedic Surgeon\n
    8. Pediatrician\n
    9. Obstetrician/Gynecologist (OB/GYN)\n
    10. Urologist\n
    11. Nephrologist (kidney)\n
    12. Psychiatrist\n
    13. Dentist\n
    14. Physiotherapist\n
    15. Ophthalmologist (Eye specialist)\n
    16. Allergist/Immunologist\n
    17. Pulmonologist (lung and respiratory)\n
    18. Endocrinologist (Hormonal)\n
    19. ENT Specialist (Ear, Nose, and Throat)\n \n
'''
def date_validate(date_obj):

    x = date_obj
    x = re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1 ', x) 
    x = re.sub(r'([a-z])(\d)', r'\1 \2', x)

    st = x.split()

    if(len(st) == 3):
        temp = st[1]
        temp = temp.upper()
        if(temp.startswith('J')):
            temp = "JANUARY"
        elif(temp.startswith('F')):
            temp = "FEBRUARY"
        elif(temp.startswith('MAR')):
            temp = "MARCH"
        elif(temp.startswith('AP')):
            temp = "APRIL"
        elif(temp.startswith('MAY')):
            temp = "MAY"
        elif(temp.startswith('JUN')):
            temp = "JUNE"
        elif(temp.startswith('JUL')):
            temp = "JULY"
        elif(temp.startswith('AU')):
            temp = "AUGUST"
        elif(temp.startswith('S')):
            temp = "SEPTEMBER"
        elif(temp.startswith('O')):
            temp = "OCTOBER"
        elif(temp.startswith('N')):
            temp = "NOVEMBER"
        elif(temp.startswith('D')):
            temp = "DECEMBER"
        st[1] = temp

    date_obj = " ".join(st)
    formats = ["%d %B %Y", "%d %B %y", "%d/%m/%y", "%d-%m-%y", "%d/%m/%Y", "%d-%m-%Y"] 

    for format in formats:
        try:
            date = datetime.strptime(date_obj, format)
            break
        except ValueError:
            date = "-1"
    
    return date if date != "-1" else "-1"
    

def new_user(request):
    request.session["user"] = True
    request.session["book_flag"] = 0
    request.session["cancel_flag"] = 0
    request.session["change_flag"] = 0
    request.session["status_flag"] = 0
    request.session["feedback"] = 0
    request.session["double_check_flag"] = 0

def finalize_booking(request):
    message = request.session['message']
    check = request.session["double_check_flag"] 
    if(check == 1):
        chatbot_response = '''Please enter the patient's full name'''
        request.session["double_check_flag"] = 2
    elif(check == 2):
        request.session['name'] = message
        chatbot_response = '''1. Male\n 2. Female\n 3. Others\n\n
        Enter appropriate option number to which the Patient's sex belong and press enter'''
        request.session["double_check_flag"] = 3
    elif(check == 3):
        if message.isdigit() and (int(message)>0 and int(message)<4):
            request.session['gender'] = int(message)
            chatbot_response = '''Please enter patient's Date of birth'''
            request.session["double_check_flag"] = 4
        else:
            chatbot_response = '''Wrong input! Please enter the appropriate option number to which the Patient's sex belong\n\n
                            1. Male\n 2. Female\n 3. Others\n\n'''
    elif (check == 4):
        date = date_validate(message)
        present_date = datetime.now()
        if(date != '-1' and date.date() < present_date.date()):
            date = date.strftime("%Y-%m-%d")
            request.session["DOB"] = date.split(' ')[0]
            chatbot_response = '''Please enter a valid phone number on which we can contact you'''
            request.session["double_check_flag"] = 5
        else:
            chatbot_response = '''Sorry! wrong input\n
                                Please enter patient's Date of birth'''
    else:
        if(len(message) == 10 and message.isdigit()):
            try:
                pat = patient_sessions.objects.latest('session_Id')
                session_Id = str(int(pat.session_Id) + 1)
            except ObjectDoesNotExist:
                session_Id = "1000001"

            name = request.session["name"]
            gender = request.session["gender"]
            dob = request.session["DOB"]
            dob = datetime.strptime(dob, "%Y-%m-%d")
            phone = message
            slot = request.session["time"]
            date_ = request.session["booking_date"]
            date_ = datetime.strptime(date_, "%Y-%m-%d")
            doctor = request.session["doc_ID"]

            try:
                patient = patient_info.objects.get(name = name, gender = gender, DOB = dob.date(), phone = phone)
                Id = patient.Id
            except ObjectDoesNotExist:
                try:
                    new_patient = patient_info.objects.latest('Id')
                    Id = str(int(new_patient.Id) + 1)
                except ObjectDoesNotExist:
                    Id = "10001"
                new_patient = patient_info(Id = Id, name = name, gender = gender, DOB = dob.date(), phone = phone)
                new_patient.save()

            doc_session, created = doctor_sessions.objects.get_or_create(doc_Id = doctor, session_date = date_.date(), session_time = slot)
            doc_session.session_count += 1
            doc_session.save()
            new_session = patient_sessions(doc_Id = doctor, session_Id = session_Id, pat_Id = Id, session_date = date_, session_time = slot)
            new_session.save()
            date_ = date_.strftime("%d-%m-%Y")    
            date_ = date_.split(' ')[0]
            
            doct = doctor_list.objects.get(Id = doctor)
            time_ = dict(doctor_sessions.time_fields).get(slot)
            chatbot_response = f'''Your appointment with Dr. {doct.name} has been booked on {date_} at {time_} and your Session Id is {session_Id}.\n
                                Please keep this Session-Id for future reference\n
                                '''
                        
            request.session.clear()
        else:
            chatbot_response = '''Sorry invalid phone number \n
            Please enter a valid phone number on which we can contact you'''

    response_data = {
        'message': chatbot_response
    }
    return JsonResponse(response_data) 

def time_check(request):
    message = request.session['message']
    if message.isdigit() and (int(message) > 0 and int(message)<=len(request.session['timmings'])):
        time_option = int(message)
        request.session["time"] = request.session['timmings'][time_option-1] 
        request.session["double_check_flag"] = 1
        request.session["book_flag"] = 9
        return finalize_booking(request)

    else :
        chatbot_response = '''Sorry the option you entered is invalid. \n
        Please enter the option of the desired time slot you wanna book and press enter \n'''
        response_data = {
            'message': chatbot_response
        }
        return JsonResponse(response_data) 
    

def time_finalize(request):
    date = date_validate(request.session["message"])
    present_date = datetime.now().date()
    present_date = present_date.strftime("%Y-%m-%d")
    present_date = datetime.strptime(present_date, "%Y-%m-%d")
    next_month_date = present_date + relativedelta(months=1)
    if(date == "-1" or (date.date() < present_date.date() or next_month_date.date() < date.date()) or ("restrict_dates" in request.session and date.strftime("%d-%m-%Y").split(' ')[0] in request.session["restrict_dates"])):
        chatbot_response = '''Sorry the date you entered is invalid. \n
                            Please enter a valid date '''
        
    else:
        Id = request.session["doc_ID"]
        
        morn = doctor_sessions.objects.filter(doc_Id = Id, session_date = date.date(), session_count = 9)
        noon = doctor_sessions.objects.filter(doc_Id = Id, session_date = date.date(), session_count = 6)
        eve = doctor_sessions.objects.filter(doc_Id = Id, session_date = date.date(), session_count = 6)

        date = date.strftime("%Y-%m-%d")
        request.session["booking_date"] = date.split(' ')[0]
        
        chatbot_response = ""
        cnt = 1
        request.session["timmings"] = []
        if len(morn) == 0:
            chatbot_response += f'''{cnt}. 10:00 AM\n'''
            cnt = cnt + 1
            request.session["timmings"].append(10)

        if len(noon) == 0:
            chatbot_response += f'''{cnt}. 02:00 PM\n'''
            cnt = cnt + 1
            request.session["timmings"].append(14)

        if len(eve) == 0:
            chatbot_response += f'''{cnt}. 05:00 PM\n'''
            cnt = cnt + 1
            request.session["timmings"].append(17)
    
        chatbot_response += '''Please enter the option of the desried time slot you wanna book and press enter \n'''
        request.session["book_flag"] = 8
    
    response_data = {
        'message': chatbot_response
    }
    return JsonResponse(response_data)            

def date_finalize(request):
    message = request.session.get("message")
    if message.isdigit() and (int(message) >0 and int(message) < 6):
        doc_option = int(message)
        Id = request.session["doctors"][doc_option-1]
        morn = doctor_sessions.objects.filter(doc_Id = Id, session_time = 10, session_count = 9)
        noon = doctor_sessions.objects.filter(doc_Id = Id, session_time = 14, session_count = 6)
        eve = doctor_sessions.objects.filter(doc_Id = Id, session_time = 17, session_count = 6)
        dates = []
        for cnt in morn:
            if(cnt in noon and cnt in eve):
                dates.append(cnt)

        restrict = ""
        doc = doctor_list.objects.get(Id = Id)
        if len(dates):
            request.session["restrict_dates"] = []
            restrict += f'''Dr. {doc.name} is not avaliable on sundays and {"he" if doc.gender == 1 else "she"} is fully booked on these particular dates \n'''
            for date in dates:
                day = date.strftime("%d-%m-%Y")
                day = day.split(' ')[0]
                restrict += f'''{day}\n'''
                request.session["restrict_dates"].append(day)
        chatbot_response += restrict
        chatbot_response = f'''\nPlease enter a valid date on which you wanna book appointment with Dr. {doc.name}\n you can only book on dates which are avaliable under one month from today \n'''
        request.session["doc_ID"] = doc.Id
        request.session["book_flag"] = 7
    
    else:
        chatbot_response = ''' Sorry! wrong input, couldn't understand,\n
        Please type in the option of the desired doctor you wanna an appointment with and press enter '''
    
    response_data = {
        'message': chatbot_response
    }
    return JsonResponse(response_data)


def doctor_selector(request):
    message = request.session.get("message")
    if message.isdigit() and (int(message) > 0 and int(message) < 20):
        doc_option = int(message)
        doctors = doctor_list.objects.filter(doc_type = doc_option)
        chatbot_response = f'''Here is the list of all {symptom_doc_matcher.doctors[doc_option-1]} available at our hospital \n
                             the payment for the booking can be done at the hospital\n'''
        request.session["doctors"] = []
        cnt=1
        for doctor in doctors:
            doc = f"{cnt}.\n"
            cnt = cnt +1
            request.session["doctors"].append(doctor.Id)
            doc+=f'name ->  {doctor.name}\n'
            sex = dict(doctor_list.gender_fields).get(doctor.gender)
            doc+=f'sex  ->  {sex}\n'
            doc+=f'experience ->  {doctor.experience} years\n'
            doc+=f'fees ->  {doctor.fees}\n'
            chatbot_response+=doc
        chatbot_response+="\n Please type in the option of the desired doctor you wanna book and press enter"
        request.session["book_flag"] = 6

    else:
        chatbot_response = f'''Sorry! wrong input, couldn't understand,\n
        {doct_types}\nPlease type in the option of the desired doctor type you wanna book an appointment with and press enter\n,
        I will display the prices and doctor names with respect to the doctor option you selected'''

    response_data = {
        'message': chatbot_response
    }
    return JsonResponse(response_data)

def doct_type_selector(request):
    chatbot_response = doct_types + '''Please type in the option of the desired doctor type you wanna book and press enter\n,
                                       I will display the prices and doctor names with respect to the doctor option you selected'''
    
    response_data = {
        'message': chatbot_response
    }
    request.session["book_flag"] = 5
    return JsonResponse(response_data)

def greet(request):
    intent = "greeting"
    if "user" in request.session:
        chatbot_response = "sorry can't understand, your request. You can ask for." + default_template
    else:
        new_user(request)
        chatbot_response = random.choice(response[intent]) + default_template

    response_data = {
        'message': chatbot_response
    }

    return JsonResponse(response_data)


def booker(request):
    if ("user" not in request.session):
        chatbot_response = "If you want to use our services through me please start by greeting me, then i would be very happy to assist you :-)"

    else :
        intent = "book_session"
        message = request.session["message"]
        book_flag = request.session["book_flag"]

        if(book_flag == 0):
            chatbot_response = '''For session/appointment booking we have two options \n\n
            1. You can book through the type of the doctor \n 
            2. You can book through by describing the symptoms you are facing \n\n 
            Please type in the option number you wanna go forward with your booking and press enter'''
            request.session["context"].append("book_session")
            request.session["book_flag"] = 1

        elif (book_flag == 1):
            if (message == '1' or message == '2'):
                if (message == '2'):
                    chatbot_response = random.choice(response[intent])
                    request.session["book_flag"] = 2
                else:
                    request.session["book_flag"] = 4
                    return doct_type_selector(request)
            else:
                chatbot_response = ''' Sorry coundn't understand your response\n
                                        For session/apoointment booking we have two options \n\n
                                        1. You can book through the type of the doctor \n 
                                        2. You can book through telling the symptoms you are facing \n\n 
                                        Please type in the option number you wanna go forward with your booking and press enter'''

        elif (book_flag == 2):
            symptoms = message
            if(pred.predict_symptom(symptoms)):
                doctor = symptom_doc_matcher.predict_doc(symptoms)
                chatbot_response = random.choice(response["symptoms"])
                request.session["doc_type"] = doctor
                chatbot_response = chatbot_response.replace("[doctor]", dict(doctor_list.doc_type).get(doctor))
                chatbot_response += '''\n 1. If you are satisfied with the type of doctor suggestion \n
                                        2. If you wanna choose the type of doctor manually\n\n
                                        Please type in the option number of the desired option you wanna choose and press enter\n'''
                request.session["book_flag"] = 3
            else:
                chatbot_response += '''Sorry cannot understand, Please describe your symptoms correctly as it is crucial part of your 
                                    session/appointment booking and getting you the best possible doctor acoording to your symptoms\n'''

        else:
            if message == '2':
                request.session["book_flag"] = 4
                return doct_type_selector(request)
            elif message == '1':
                request.session["book_flag"] = 5
                request.session["message"] = request.session["doc_type"]
                return doctor_selector(request)
            else:
                chatbot_response = '''Sorry! wrong input, couldn't understand,\n
                                    1. If you are satisfied with the type of doctor suggestion \n
                                    2. If you wanna choose the type of doctor manually\n\n
                                    Please type in the option number of the desired option you wanna choose and press enter\n'''              


    response_data = {
        "message": chatbot_response
    }
    return JsonResponse(response_data)       


def canceler(request):
    if "user" not in request.session:
        chatbot_response = "If you want to use our services through me please start by greeting me, then i would be very happy to assist you :-)"
    else:
        intent = "session_cancelation"
        message = request.session["message"]
        cancel_flag = request.session["cancel_flag"]
        if(cancel_flag == 0):
            chatbot_response = random.choice(response["session_cancelation"])
            request.session["cancel_flag"] = 1
        elif(cancel_flag == 1):
            if(message.isdigit() and len(message) == 7):
                try:
                    session_Id = patient_sessions.objects.get(Session_Id = message)
                    request.session["session_Id"] = session_Id
                    chatbot_response = '''Are you sure you want to cancel your appointment\n
                                        1. YES\n
                                        2. No\n
                                        Please type in the option number of the desired option you wanna choose and press enter\n'''
                    request.session["cancel_flag"] = 2              
                except:
                    chatbot_response = '''Sorry! No record found.\n
                                    Please enter a valid session Id'''
            else:
                chatbot_response = '''Wrong session Id.\n
                            Please enter a valid session Id'''
        else:
            if(message == '1'):
                session_delete = patient_sessions.objects.get(session_Id = request.session["session_Id"])
                doc_session = doctor_sessions.objects.get(doc_Id = session_delete.doc_Id, session_date = session_delete.session_date, session_time = session_delete.session_time)
                doc_session.session_count -=1
                session_delete.delete()
                doc_session.save()
                request.session.clear()
                chatbot_response = "Your session has been successfully cancelled"
            elif(message == '2'):
                chatbot_response = "Sure, your session stays the same"
                request.session.clear()
            else:
                chatbot_response = '''Sorry! wrong input, couldn't understand.\n
                                    1. YES\n
                                    2. No\n
                                    Please type in the option number of the desired option you wanna choose and press enter\n'''

    response_data = {
        "message": chatbot_response
    }
    return JsonResponse(response_data)

def feedbacker(request):
    if "user" not in request.session:
        chatbot_response = "If you want to use our services through me please start by greeting me, then i would be very happy to assist you :-)"
    else:
        intent = "feedback"
        message = request.session["message"]
        feed_flag = request.session["feedback"]
        if(feed_flag == 0):
            chatbot_response = random.choice(request.session["feedback"])
            request.session["feedback"] = 1
        else:
            chatbot_response = '''Thank you for your valuable feedback, we will work for it and continue to improve our services\n'''

    response_data = {
        "message": chatbot_response
    }
    return JsonResponse(response_data)

def changer(request):
    pass


def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '')
        user = data.get('sessionid', '')
        print(user)
        
        # insert code to identify if it is an ongoing session
        request.session['message'] = user_message
        if("book_flag" in request.session):
            book_flag = request.session["book_flag"]
            if book_flag:
                if book_flag <=3:
                    print("called booker")
                    return booker(request)
                elif book_flag == 4:
                    print("called doct_type_selector")
                    return doct_type_selector(request)
                elif book_flag == 5:
                    print("called doctor_selector")
                    return doctor_selector(request)
                elif book_flag == 6:
                    print("called date_finalize")
                    return date_finalize(request)
                elif book_flag == 7:
                    print("called time_finalize")
                    return time_finalize(request)
                elif book_flag == 8:
                    print("called time_check")
                    return time_check(request)
                elif book_flag == 9:
                    print("called finalize_booking")
                    return finalize_booking(request)
            

        intent = pred.predict_intent(user_message)

        intent_func = {
            "greeting": greet,
            "book_session": booker,
        }

        return intent_func[intent](request)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
