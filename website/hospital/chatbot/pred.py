import google.generativeai as genai
import os

genai.configure(api_key=os.environ["best_offer"])

common_prompt = '''so i want you to recognise the intent of the sentence on the basis of a hospital website chatbot, and the intents are,
a = "asking to book a doctors appointment/session", 
b = "reschedule a previous booked appointment/session", 
c = "cancel a previous booked apointment/session", 
d = "if the person is tring to greet the chatbot",
e = "if the person is trying to provide a feedback/complaint of an earlier hospital visit", 
f = "or the intent is not matching to niether these previous intents and it is a sentense not related to this topic basically a fallback intent",
based on the above info only respond if it is a, b, c, d, e or f intent as i mentioned above, the sentence is "{intent}" '''

intents = {'a' : 'book_session', 'b' : 'session_reschedule', 'c' : 'session_cancelation', 'd' : 'greeting', 'e' : 'feedback', 'f' : 'fallback'}

def predict_intent(text):
    full_prompt = common_prompt.format(intent=text)
    response = genai.generate_text(prompt=full_prompt)
    ans = response.result.strip().lower().replace('*','')
    intents[ans]