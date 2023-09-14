import tensorflow as tf
import tensorflow_text as text
from tensorflow import keras
import tensorflow_hub as hub
from keras.models import load_model
import numpy as np

model = load_model(("E:/hospital-response/chatbot/models/final_h5.h5"), custom_objects={'KerasLayer':hub.KerasLayer}, compile=False)
intents = ['fallback','service_completion','greeting','session_reschedule','session_cancelation','book_session','feedback', 'session_status']

sym_model = load_model(("E:/hospital-response/chatbot/models/symptom_h5.h5"), custom_objects={'KerasLayer':hub.KerasLayer}, compile=False)

def predict_intent(text):
    x = model.predict([text])
    ind = np.argmax(x)
    return intents[ind]

def predict_symptom(text):
    x = sym_model.predict([text])
    return 1 if x < 0.5 else 0