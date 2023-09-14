import openai
import langchain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI

key = "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"
llm = OpenAI(temperature=0.3, openai_api_key=key)

prompt = PromptTemplate.from_template("what type of doctor should i suggest if {symptoms}")
chain = LLMChain(llm = llm, prompt=prompt)

doctors = ["General Practitioner", "Physician", "Cardiologist", "Gastroenterologist", "Dermatologist", "Neurologist", "Orthopedic Surgeon", "Pediatrician", "Gynecologist", "Urologist", "Nephrologist", "Psychiatrist", "Dentist", "Physiotherapist", "Ophthalmologist", "Allergist/Immunologist", "Pulmonologist", "Endocrinologist", "ENT Specialist (Ear, Nose, and Throat)"]


def predict_doc(symptoms):
    chain.run("i am suffering from blurry vission")

