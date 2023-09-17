from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI

key = "bhaag_bsdk"
llm = OpenAI(temperature=0.3, openai_api_key=key)

prompt = PromptTemplate.from_template("what type of doctor should i suggest if, {symptoms}")
chain = LLMChain(llm = llm, prompt=prompt)

doctors = ["practitioner", "physician", "cardiologist", "gastroenterologist", "dermatologist", "neurologist", "orthopedic", "pediatrician", "gynecologist", "urologist", "nephrologist", "psychiatrist", "dentist", "physiotherapist", "ophthalmologist", "allergist", "immunologist", "pulmonologist", "endocrinologist", "ent"]
doctors_ = ["General Practitioner", "Physician", "Cardiologist", "Gastroenterologist", "Dermatologist", "Neurologist", "Orthopedic Surgeon", "Pediatrician", "Gynecologist", "Urologist", "Nephrologist", "Psychiatrist", "Dentist", "Physiotherapist", "Ophthalmologist", "Allergist/Immunologist", "Pulmonologist", "Endocrinologist", "ENT Specialist"]

def predict_doc(symptoms):
    ans = chain.run(symptoms)
    ans = ans.lower()

    i=1
    for doctor in doctors:
        if doctor == "immunologist":
            i = i-1
        if doctor in ans:
            return i
        
    return 1
    

