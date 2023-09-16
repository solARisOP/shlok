import openai
import langchain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI

key = "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"
llm = OpenAI(temperature=0.3, openai_api_key=key)

prompt = PromptTemplate.from_template("what type of doctor should i suggest if {symptoms}")
chain = LLMChain(llm = llm, prompt=prompt)

doctors = ["practitioner", "physician", "cardiologist", "gastroenterologist", "dermatologist", "neurologist", "orthopedic", "pediatrician", "gynecologist", "urologist", "nephrologist", "psychiatrist", "dentist", "physiotherapist", "ophthalmologist", "allergist", "immunologist", "pulmonologist", "endocrinologist", "ent"]

def predict_doc(symptoms):
    ans = chain.run("i am suffering from blurry vission")
    ans = ans.lower()

    i=1
    for doctor in doctors:
        if doctor == "immunologist":
            i = i-1
        if doctor in ans:
            return i
        
    return 1
    

