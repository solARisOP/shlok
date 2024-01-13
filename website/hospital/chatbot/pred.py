from langchain.llms.google_palm import GooglePalm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

llm = GooglePalm(google_api_key = os.environ["best_offer_2"])

intent_prompt = PromptTemplate.from_template('''so i want you to recognise the intent of the sentence on the basis of a hospital website chatbot, and the intents are,
a = "asking to book a doctors appointment/session", 
b = "reschedule a previous booked appointment/session", 
c = "cancel a previous booked apointment/session", 
d = "if the person is tring to greet the chatbot",
e = "if the person is trying to provide a feedback/complaint of an earlier hospital visit", 
f = "or the intent is not matching to niether these previous intents and it is a sentense not related to this topic basically a fallback intent",
based on the above info please tell me if it is a, b, c, d, e or f intent as i mentioned above, the sentence is "{intent}" ''')

intents = {'a' : 'book_session', 'b' : 'session_reschedule', 'c' : 'session_cancelation', 'd' : 'greeting', 'e' : 'feedback', 'f' : 'fallback'}

def predict_intent(text):
    chain = LLMChain(llm = llm, prompt= intent_prompt)
    ans = chain.run(text)
    return intents[ans]