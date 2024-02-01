from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.openai import OpenAI
import os

llm = OpenAI(temperature=0.3, openai_api_key=os.environ['best_offer'], model=os.environ["model"])

prompt = PromptTemplate.from_template('''check the following sentence and if the sentence is about medical symptoms then tell me what type of doctor
 should i suggest and the doctor type should be among these("General practitioner", "physician", "cardiologist", "gastroenterologist", "dermatologist",
 "neurologist", "orthopedic", "pediatrician", "gynecologist", "obstetrician", "urologist", "nephrologist", "psychiatrist", "dentist", "maxillofacial",
 "physiotherapist", "ophthalmologist", "allergist", "immunologist", "pulmonologist", "endocrinologist", "ENT Specialist") or if the sentence is not about
 symptoms say 'nope'. The sentence is '{symptoms}' ''')

chain = LLMChain(llm = llm, prompt=prompt)

doctors = ["general practitioner", "physician", "cardiologist", "gastroenterologist", "dermatologist", "neurologist", "orthopedic", "pediatrician", "gynecologist", "obstetrician", "urologist", "nephrologist", "psychiatrist", "dentist", "maxillofacial", "physiotherapist", "ophthalmologist", "allergist", "immunologist", "pulmonologist", "endocrinologist", "ent specialist"]

def predict_doc(symptoms):
    ans = chain.run(symptoms)
    ans = ans.strip()
    ans = ans.lower()
    
    if ans == 'nope':
        return 0
    
    ind = doctors.index(ans)
    if ans == "immunologist" or ans == "obstetrician" or ans == "maxillofacial":
        ind-=1
    return ind+1
    

