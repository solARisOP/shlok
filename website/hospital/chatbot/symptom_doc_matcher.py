from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os

llm = GoogleGenerativeAI(google_api_key = os.environ["best_offer"], model=os.environ["model"])

prompt = PromptTemplate.from_template('''check the following sentence and if the sentence is about medical symptoms then tell me what type of doctor
 should i suggest and the doctor type should be among these("General practitioner", "physician", "cardiologist", "gastroenterologist", "dermatologist",
 "neurologist", "orthopedic", "pediatrician", "gynecologist", "obstetrician", "urologist", "nephrologist", "psychiatrist", "dentist", "maxillofacial",
 "physiotherapist", "ophthalmologist", "allergist", "immunologist", "pulmonologist", "endocrinologist", "ENT Specialist")based on the above info only respond in the intents as I mentioned above,
  or if the sentence is not about symptoms say 'nope'. The sentence is '{symptoms}' ''')

doctors = ["general practitioner", "physician", "cardiologist", "gastroenterologist", "dermatologist", "neurologist", "orthopedic", "pediatrician", "gynecologist", "obstetrician", "urologist", "nephrologist", "psychiatrist", "dentist", "maxillofacial", "physiotherapist", "ophthalmologist", "allergist", "immunologist", "pulmonologist", "endocrinologist", "ent specialist"]

def predict_doc(symptoms):
    chain = prompt | llm
    ans = chain.invoke(symptoms).strip().lower().replace('*','')
    
    if ans == 'nope':
        return 0
    
    ind = doctors.index(ans)
    if ans == "immunologist" or ans == "obstetrician" or ans == "maxillofacial":
        ind-=1
    return ind+1
    

