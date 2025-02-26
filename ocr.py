
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import re
import datetime

from services.docs_to_base64 import convert_to_base64, pdf_to_base64

load_dotenv()

model = "models/gemini-2.0-flash"
llm = ChatGoogleGenerativeAI(
    model=model,
    google_api_key=os.environ["GEMINI_API_KEY"],
)
parser = JsonOutputParser()

prompt_template = PromptTemplate(
    template=(
        "Você deve identificar o tipo de documento fornecido e extrair todas as informações contidas nele. "
        "Responda **apenas** com um JSON válido, sem qualquer explicação. "
        "Se for um comprovante de residência, extraia apenas o endereço. "
        "Se for CNH, RG ou CRLV, capture todas as informações relevantes. "
        "Não omita nenhum dado e preserve a formatação conforme encontrada no documento. "
        "Aqui está o formato esperado:\n\n"
        "{format_instructions}"
    ),
    input_variables=[],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


def extract_json_from_response(response_text):
    match = re.search(
        r"\{.*\}", response_text, re.DOTALL
    )  
    if match:
        return json.loads(match.group(0)) 
    else:
        raise ValueError("Nenhum JSON válido encontrado na resposta do modelo.")


def classify_and_extract_data(file_path: str):
    file_extension = os.path.splitext(file_path)[-1].lower()
    if file_extension in [".pdf"]:
        base64_image = pdf_to_base64(file_path)
    elif file_extension in [".jpeg", ".jpg", ".png"]:
        base64_image = convert_to_base64(file_path)
    else:
        raise ValueError("Formato de arquivo não suportado")

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt_template.format()},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"},
            },
        ]
    )

    response = llm.invoke([message])
    response_text = response.content
    parsed_data = extract_json_from_response(response_text)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    with open(f"./extracted_datas/extracted_data_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=4, ensure_ascii=False)


file_path = "./docs/seu_arquivo.pdf"
classify_and_extract_data(file_path)
