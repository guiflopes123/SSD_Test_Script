import pathlib
import textwrap
import google.generativeai as genai
import subprocess
import sys
import os
import pandas as pd

# NOTE: Your prompt contains media inputs that are not directly supported by the
# Gemini Files API. Preprocessing will be required for these inputs. Specific
# information is provided below.

"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

#os.environ["YOUR_API_KEY"] = ""
genai.configure(api_key="")
# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

def AI_analysis(file_path, current_time):
    
    base_dir = os.path.dirname(__file__)
    log_dir = os.path.join(base_dir, "Log")
    output_filename = f"{log_dir}/{file_path}"
    with open(output_filename, 'r') as f:
        file_content = f.read()

    chat_session = model.start_chat(
    history=[
        {
        "role": "user",
        "parts": [
            "Com base no log fornecido, você é um analisador de teste para memória NVME, me resuma o log e analise os dados visando encontrar possíveis problemas na memória, cada item de teste está identificado pcomo (Disk: (nome da memória) Test Item: (item de teste), Test Result: (resultado do teste)), Para cada item de teste encontrado resumir separadamente o seu resultado e os dados coletados. Iniciar o log com a data atual com hora, minuto e segundos fornecidos pela variavel current_time. O primeiro item do resumo se chama Resumo do Teste, onde há uma lista de quais testes foram feitos com seus resultados, a saída deve ser um relatório em inglês.",
            file_content, current_time
            
        ],
        },
             
    ]
    )

    response = chat_session.send_message("Analise o log")

    # Salva a análise do Gemini em um novo arquivo AI_Analysis.txt

    with open(f"{log_dir}/AI_Gemini_{file_path}", "w") as output_file:
        output_file.write(response.text)

    print(f"Análise do Gemini salva em AI_Analysis.txt")
    print(chat_session.history)
    return True



model = genai.GenerativeModel(
  model_name="gemini-1.5-pro-latest",
  safety_settings=safety_settings,
  generation_config=generation_config,
)

if __name__ == "__main__":
    if len(sys.argv) != 3:
      print("Erro ao passar os argumentos. Use: python script.py caminho/para/arquivo.txt")
      sys.exit(1)

    file_path = sys.argv[1]
    current_time = sys.argv[2]
    #file_path = "nvme0n1_2024-06-27_13-58-29.txt"
    Generated_AR = AI_analysis(file_path,current_time)
    #file_path = "nvme0n1_2024-05-24_14-09-29.txt"

    