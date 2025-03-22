from keys import GEMINI
import google.generativeai as genai
from json import loads
from re import search


def generate_text(opts):
    """
     opts = {
        "text":    "Fale sobre a teoria da relatividade", 
        "context": "será usado em um trabalho academico "
        "instructions": "deve estar nas forma abnt, utilize artigos cientificos recentes"
    }
    """
    genai.configure(api_key=GEMINI["API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash-002")
    response = model.generate_content(f"{opts["text"]}.\ncontexto: {opts["context"]}.\ninstrução:{opts["instructions"]}")
    return response.text

def transform_to_dict(data):
    tmp = data.replace("json","").replace("```","")
    return loads(tmp)