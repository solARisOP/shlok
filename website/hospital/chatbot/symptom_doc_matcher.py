import google.generativeai as genai
import os

genai.configure(api_key=os.environ["best_offer"])
model = genai.GenerativeModel('gemini-1.5-flash')

common_prompt = '''check the following sentence and if the sentence is about medical symptoms then tell me what type of doctor
 should i suggest and the doctor type should be among these("General practitioner", "physician", "cardiologist", "gastroenterologist", "dermatologist",
 "neurologist", "orthopedic", "pediatrician", "gynecologist", "obstetrician", "urologist", "nephrologist", "psychiatrist", "dentist", "maxillofacial",
 "physiotherapist", "ophthalmologist", "allergist", "immunologist", "pulmonologist", "endocrinologist", "ENT Specialist")based on the above info only respond in the intents as I mentioned above,
  or if the sentence is not about symptoms say 'nope'. The sentence is '{symptoms}' '''

doctors = ["general practitioner", "physician", "cardiologist", "gastroenterologist", "dermatologist", "neurologist", "orthopedic", "pediatrician", "gynecologist", "obstetrician", "urologist", "nephrologist", "psychiatrist", "dentist", "maxillofacial", "physiotherapist", "ophthalmologist", "allergist", "immunologist", "pulmonologist", "endocrinologist", "ent specialist"]

def predict_doc(symptoms):
    full_prompt = common_prompt.format(symptoms=symptoms)
    response = model.generate_content(full_prompt)
    ans = response.candidates[0].content.parts[0].text.strip().lower().replace('*', '')
    
    if ans == 'nope':
        return 0
    
    ind = doctors.index(ans)
    if ans == "immunologist" or ans == "obstetrician" or ans == "maxillofacial":
        ind-=1
        
    return ind+1



