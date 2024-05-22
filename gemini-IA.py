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

#os.environ["YOUR_API_KEY"] = "AIzaSyCfWPLk7Hc3VI_PgWi4p3Fzjlm-cIub4r4"
genai.configure(api_key="AIzaSyD2HJu1KzyvGB-6GILSz3kaKdfenl7nRI4")
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

def AI_analysis(file_path):
    
    base_dir = os.path.dirname(__file__)
    log_dir = os.path.join(base_dir, "Log")
    output_filename = f"{log_dir}/{file_path}"
    with open(output_filename, 'r') as f:
        log_text = f.read()

    chat_session = model.start_chat(
    history=[
        {
        "role": "user",
        "parts": [
            "Com base no log fornecido, você é um analisador de teste para memória NVME, me resuma o log e analise os dados visando encontrar possíveis problemas na memória, cada item de teste está identificado pcomo (Disk: (nome da memória) Test Item: (item de teste), Test Result: (resultado do teste)), Para cada item de teste encontrado resumir separadamente o seu resultado e os dados coletados. O primeiro item do resumo se chama Resumo do Teste, onde há umalista de quais testes foram feitos com seus resultados{file_content}",
            log_text
        ],
        },
        {
      "role": "model",
      "parts": [
        "## Resumo do Teste NVMe para memória: \n\n**Data e Hora do Teste:\n\n**Testes Realizados e Resultados:**\n\n* **SMART_Log:** PASS\n\n\n\n## Detalhes dos Testes:\n\n**1. SMART_Log:**\n\n* **Resultado:** PASS\n* **Observações:**\n    * Nenhum alerta crítico encontrado no log SMART.\n    * Temperatura da Memória: 22°C (dentro da faixa normal)\n    * Disponibilidade de Spare: 100% (excelente)\n    * Porcentagem de Uso: 0% (novo ou pouco usado)\n    * Número de Erros de Mídia: 0 (nenhum erro encontrado) \n\n## Análise Geral:\n\nCom base nos resultados do log, a memória NVMe nvme0n1 parece estar funcionando **corretamente** sem apresentar problemas. Todos os testes realizados foram concluídos com sucesso e os indicadores SMART estão dentro dos parâmetros esperados. \n\n## Recomendações:\n",
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
    if len(sys.argv) != 2:
        print("Erro ao passar os argumentos. Use: python script.py caminho/para/arquivo.txt")
        sys.exit(1)

    file_path = sys.argv[1]
    Generated_AR = AI_analysis(file_path)
    #file_path = "nvme0n1_2024-05-21_09-02-39.txt"

    