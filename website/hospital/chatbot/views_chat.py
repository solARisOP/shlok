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

file_path = "chatbot/responses.json"
with open(file_path, 'r') as json_file:
    response = json.load(json_file)

default_template = '''\n
"Booking your new appointment" \n
"Cancel your appointment" \n
"Reschedule your appointment" \n
"Providing a feedback about your last visit" \n
Please let me know about your request.
 '''

doct_types = '''General Practitioner (GP)\n
    Physician\n
    Cardiologist\n
    Gastroenterologist\n
    Dermatologist\n
    Neurologist\n
    Orthopedic Surgeon\n
    Pediatrician\n
    Obstetrician/Gynecologist (OB/GYN)\n
    Urologist\n
    Nephrologist (kidney)\n
    Psychiatrist\n
    Dentist\n
    Physiotherapist\n
    Ophthalmologist (Eye specialist)\n
    Allergist/Immunologist\n
    Pulmonologist (lung and respiratory)\n
    Endocrinologist (Hormonal)\n
    ENT Specialist (Ear, Nose, and Throat)\n \n
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
        elif(temp.startswith('JUNE')):
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
    request.session["context"] = []
    request.session["user_symptoms"] = ""
    request.session["book_flag"] = 0
    request.session["cancel_flag"] = 0
    request.session["change_flag"] = 0
    request.session["double_check_flag"] = 0

def finalize_booking(request):
    message = request.session['message']
    time_option = int(message)
    if request.session["double_check_flag"] > 0 or (message.isdigit() and (time_option>0 and time_option<=len(request.session['timmings']))):
        check = request.session["double_check_flag"] 
        if(check == 0):
            request.session["time"] = int(message) 
            request.session["double_check_flag"] == 1
        elif(check == 1):
            chatbot_response = '''Please enter the patient's full name'''
            request.session["double_check_flag"] == 2
        elif(check == 2):
            request.session['name'] = message
            chatbot_response = '''1. Male\n 2. Female\n 3. Others\n\n
            Enter appropriate option number to which the Patient's sex belong and press enter'''
            request.session["double_check_flag"] == 3
        elif(check == 3):
            if message.isdigit() and (int(message)>0 and int(message)<4):
                request.session['gender'] = int(message)
                chatbot_response = '''Please enter patient's Date of birth'''
                request.session["double_check_flag"] == 4

            else:
                chatbot_response = '''Wrong input! Please enter the appropriate option number to which the Patient's sex belong\n\n
                                1. Male\n 2. Female\n 3. Others\n\n'''
        elif (check == 4):
            date = date_validate(message).date()
            present_date = datetime.now().date()
            if(date != '-1' and date < present_date):
                date = date.strftime("%Y-%m-%d")
                request.session["DOB"] = date
                chatbot_response = '''Please enter a valid phone number on which we can contact you'''
                request.session["double_check_flag"] == 5
            else:
                chatbot_response = '''Sorry! wrong input\n
                                    Please enter patient's Date of birth'''
        else:
            if(len(message) == 10 and message.isdigit()):
                request.session["double_check_flag"] == 0
                request.session["book_flag"] =0
                pat = patient_sessions.objects.latest('session_Id')
                if(pat is None):
                    Id = "10001"
                else:
                    Id = str(int(pat.session_Id) + 1)
                chatbot_response = ''''''

            else:
                chatbot_response = '''Sorry invalid phone number \n
                Please enter a valid phone number on which we can contact you'''

    else :
        chatbot_response = '''Sorry the option you entered is invalid. \n
        Please enter the option of the desired time slot you wanna book and press enter \n'''

def time_finalize(request):
    date = date_validate(request.session["message"])
    present_date = datetime.now().date()
    present_date = present_date.strftime("%Y-%m-%d")
    next_month_date = present_date + relativedelta(months=1)
    if(date == "-1" or (date.date() < present_date.date() and next_month_date.date() < date.date())):
        chatbot_response = '''Sorry the date you entered is invalid. \n
                            Please enter a valid date '''
        
    else:
        Id = request.session["doc_ID"]
        date = date.strftime("%Y-%m-%d")
        request.session["booking_date"] = date
        
        morn = doctor_sessions.objects.filter(doc_Id = Id, session_date = date, session_count = 9)
        noon = doctor_sessions.objects.filter(doc_Id = Id, session_date = date, session_count = 6)
        eve = doctor_sessions.objects.filter(doc_Id = Id, session_date = date, session_count = 6)
        
        chatbot_response = ""
        cnt = 1
        request.session["timmings"] = []
        if(len(morn) == 0):
            chatbot_response += f'''{cnt}. 10:00 AM\n'''
            cnt = cnt + 1
            request.session["timmings"].append(10)

        if(len(noon) == 0):
            chatbot_response += f'''{cnt}. 02:00 PM\n'''
            cnt = cnt + 1
            request.session["timmings"].append(14)

        if(len(eve) == 0):
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
    doc_option = int(message)
    if message.isdigit() and (doc_option >0 and doc_option < 6):
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
            restrict += f'''Dr. {doc.name} is not avaliable on sundays and {"he" if doc.gender == 1 else "she"} is fully booked on these particular dates \n'''
            for date in dates:
                restrict += f'''{date.strftime("%d-%m-%Y")}\n'''
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
    doc_option = int(message)
    if doc_option.isdigit() and (doc_option > 0 and doc_option < 20):
        doctors = doctor_list.objects.filter(doct_type = doc_option)
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
        request.session["context"].append(intent)
        chatbot_response = random.choice(response[intent]) + default_template

    response_data = {
        'message': chatbot_response
    }

    return JsonResponse(response_data)


def booker(request):
    if ("user" not in request.session):
        chatbot_response = "If you want to use our services through me please start by greeting me, then i would be very happy to assist you :-)"

    else :
        current_context = request.session["context"][-1]
        intent = "book_session"
        message = request.session["message"]
        book_flag = request.session["book_flag"]

        if(current_context == "greeting"):
            chatbot_response = '''For session/appointment booking we have two options \n\n
            1. You can book through the type of the doctor \n 
            2. You can book through by describing the symptoms you are facing \n\n 
            Please type in the option number you wanna go forward with your booking and press enter'''
            request.session["context"].append("book_session")
            request.session["book_flag"] = 1

        elif (current_context == intent and book_flag == 1):
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

        elif (current_context == intent and book_flag == 2):
            request.session["user_symptoms"].append(message)
            if(pred.predict_symptom(request.session["user_symptoms"])):
                doctor = symptom_doc_matcher.predict_doc(request.session["user_symptoms"])
                chatbot_response += random.choice(response["symptoms"])
                chatbot_response = chatbot_response.replace("[doctor]", doctor)
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
                return doctor_selector(request)
            else:
                chatbot_response = '''Sorry! wrong input, couldn't undersatnd,\n
                                    1. If you are satisfied with the type of doctor suggestion \n
                                    2. If you wanna choose the type of doctor manually\n\n
                                    Please type in the option number of the desired option you wanna choose and press enter\n'''              


    response_data = {
        "message": chatbot_response
    }
    return JsonResponse(response_data)       


def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '')
        user = data.get('sessionid', '')
        print(user)

        response_data = {
            "message": "hi"
        }
        request.session["message"] = user_message
        return JsonResponse(response_data)     
        
        

        # insert code to identify if it is an ongoing session

        intent = pred.predict_intent(user_message)

        intent_func = {
            "greeting": greet,
            "book_session": booker,
        }

        return intent_func[intent](request)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
