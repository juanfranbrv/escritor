"""
Archivo principal del proyecto escritor.
Refactorización de este proyecto:
https://github.com/samwit/agent_tutorials/blob/main/agent_write/tools.py
https://www.youtube.com/watch?v=nK9K8UPraXk&t=2s

"""

import os
from dotenv import load_dotenv

# typing es un módulo incorporado en Python Proporciona herramientas para la anotación de tipos.
# TypedDict es una herramienta para crear tipos de datos personalizados que se comportan como diccionarios.
from typing_extensions import TypedDict
from typing import List

# Importar las clases para interactuar con los diferentes LLMs a través de LangChain.
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import StateGraph, END

from rich import print

# ════════════════════════════════════════════════
# ESTADO
# ════════════════════════════════════════════════


class GraphState(TypedDict):
    """
    Representa el estado del grafo

    """

    tema: str
    plan: str
    numero_de_pasos: int
    texto_ya_escrito: str
    texto_final: str
    secciones: List[str]
    numero_de_palabras: int  # Este es el numero de palabras que se han generado
    modelo: str
    


# ════════════════════════════════════════════════
# SETTINGS
# ════════════════════════════════════════════════
MODELO_LLM = 1  # 1=openai gpt-4o-mini,  2=GroqDeepSeek, 3=Gemini
TEMA = "Ayuno intermitente en hombres mayores de 50 años"
PALABRAS = 400


# ════════════════════════════════════════════════
# FUNCIONES DE UTILIDAD
# ════════════════════════════════════════════════

from tools import write_markdown_file, contar_palabras, human_in_the_loop


# ════════════════════════════════════════════════
# NODOS
# ════════════════════════════════════════════════


def nodo_planificador(state):
    """
    Toma el prompt inicial y devuelve un plan para
    redactar un documento extenso
    """

    print("\n\n[bold green]--- Entrando en el nodo planificador---\n[/bold green]")

    tema = state["tema"]

    numero_de_pasos = state["numero_de_pasos"]
    numero_de_pasos += 1

    plan = cadena_planificador.invoke({"tema": tema, "PALABRAS": PALABRAS})

    # Dividir el plan en secciones, asumiendo que están separadas por "---"
    secciones = [
        seccion.strip() for seccion in plan.strip().split("---") if seccion.strip()
    ]
    print(f"Secciones generadas: ({len(secciones)})\n{secciones}\n\n")
    print(f"[]")

    human_in_the_loop()

    return {
        "secciones": secciones,
        "numero_de_pasos": numero_de_pasos,
        "plan": plan,
        "texto_ya_escrito": "",
    }



# --------------------------------------------
def nodo_escritor(state):
    """
    Redacta un parrafo
    """

    print("\n\n--- Entrando en nodo escritor ---\n")

    tema = state["tema"]
    secciones = state["secciones"]  # Obtenemos la lista de secciones del estado
    numero_de_pasos = int(state["numero_de_pasos"])
    numero_de_pasos += 1

    acumulador_texto = ""

    for idx, seccion in enumerate(secciones):  # Iteramos sobre la lista de secciones
        resultado = cadena_escritor.invoke(
            {
                "tema": tema,
                "plan": str(
                    secciones
                ),  # Seguimos pasando el plan completo para contexto, aunque ahora tenemos secciones. Podemos refinar esto después.
                "texto_ya_escrito": acumulador_texto,
                "seccion": seccion,  # Pasamos el enunciado de la sección actual
            }
        )
        acumulador_texto += resultado + "\n\n"
        print(
            f"Texto seccion {idx+1}: {resultado}\n numero de palabras: {contar_palabras(resultado)}\n"
        )
        human_in_the_loop()

    numero_de_palabras = contar_palabras(acumulador_texto)
    print(f"Total de palabras: {numero_de_palabras}")
    print(f"Documento final generado con {numero_de_palabras} palabras.")

    return {
        "texto_final": acumulador_texto,
        "numero_de_palabras": numero_de_palabras,
        "numero_de_pasos": numero_de_pasos,
    }


# ------------------------------------------------
def nodo_guardador(state):
    """
    Toma el documento finalizado y lo guarda en el disco
    """
    print("\n\n[bold magenta]--- Guardando el documento ---[/bold magenta]\n\n")

    plan = state["plan"]
    modelo = state["modelo"]
    numero_de_palabras = state["numero_de_palabras"]
    numero_de_pasos = int(state["numero_de_pasos"])
    numero_de_pasos += 1

    documento_final = (
        state["texto_final"] + f"\n\n Total palabras: {numero_de_palabras}"
    )  # Usamos el documento final del estado

    write_markdown_file(documento_final, f"documento_final_{modelo}")
    write_markdown_file(plan, f"plan_{modelo}")

    return {"numero_de_pasos": numero_de_pasos}


# ════════════════════════════════════════════════
# CREAMOS EL GRAFO
# ════════════════════════════════════════════════
def crear_grafo():

    workflow = StateGraph(GraphState)

    workflow.add_node("nodo_planificador", nodo_planificador)
    workflow.add_node("nodo_escritor", nodo_escritor)
    workflow.add_node("nodo_guardador", nodo_guardador)

    workflow.set_entry_point("nodo_planificador")

    workflow.add_edge("nodo_planificador", "nodo_escritor")
    workflow.add_edge("nodo_escritor", "nodo_guardador")
    workflow.add_edge("nodo_guardador", END)

    return workflow.compile()


if __name__ == "__main__":

    os.system("cls")

    # ════════════════════════════════════════════════
    # Cargamos las APIkey y configuramos el LLM
    # ════════════════════════════════════════════════
    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    match MODELO_LLM:
        case 1:
            LLM = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=1)
        case 2:
            LLM = ChatGroq(
                model="deepseek-r1-distill-llama-70b",
                api_key=GROQ_API_KEY,
                temperature=1,
            )
        case 3:
            LLM = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", api_key=GOOGLE_API_KEY, temperature=1
            )

    # ════════════════════════════════════════════════
    # CADENAS
    # ════════════════════════════════════════════════
    with open("prompt_plan.txt", "r") as file:
        plan_template = file.read()

    plan_prompt_template = ChatPromptTemplate([("system", ""), ("user", plan_template)])
    cadena_planificador = plan_prompt_template | LLM | StrOutputParser()

    with open("prompt_escritor.txt", "r") as file:
        escritor_template = file.read()

    escritor_prompt_template = ChatPromptTemplate(
        [("system", ""), ("user", escritor_template)]
    )
    cadena_escritor = escritor_prompt_template | LLM | StrOutputParser()

    app = crear_grafo()

    prompt = {"tema": TEMA, "numero_de_pasos": 0, "modelo": "gpt-4o-mini"}

    print("[bold green]Inicio del proceso...[/bold green]")
    print("-----------------------------------")
    print(f"Tema: {TEMA}")
    print(f"Modelo seleccionado: {MODELO_LLM}")

    resultado = app.invoke(prompt)

    print("\n\n--- Resultado final ---\n")
    print(f"[bold yellow]Resultado: {resultado}[/bold yellow]")
