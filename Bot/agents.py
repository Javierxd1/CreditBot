from typing import Literal,TypedDict
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import MessagesState, StateGraph, START, END

load_dotenv()
llm = ChatOpenAI(model='gpt-4o',
                 temperature= 0.2,
                 api_key= os.getenv("OPENAI_API_KEY"),
                 max_tokens = 400)

class State(MessagesState):

    edad:int 
    ingresos:int 
    score:int 
    justificación:str 
    region:str 
    cliente_antiguo: Literal['Si','No'] 


#Instrucciones para el LLM
recomendaciones = SystemMessage(
    content= """
    Actua como un experto en finanzas personales. Si la persona tiene una edad entre menor a 21 años, brindale un par de consejos
    para tener unas finanzas personales existosas. Además, cuentale lo que debe tener en cuenta para un crédito.

    Si la persona es mayor a 70 años, dile de manera muy respetuosa que no puede acceder a una crédito. Explicale de manera muy
    cordial las dificulates de prestar un crédito debido a su edad.

    Responde unicamente teniendo en cuenta la edad de quién ingresa la respuesta.
    """
)

politicas = SystemMessage(
    content= """
    <role> Eres un agente experto en asinganción de creditos para una fintech. </role>
    <task> Tienes la tarea de aprobar o denegar las solicitudes. Tendrás unas polìticas puntuales que te ayudan a determinar la decisión final.
    De acuedo con el contexo responder al cliente si el credito ha sido o no aprobado
    </task>
    <context>
    A continuación tienes las políticas específicadas.
    1. Verifica que el solicitante tenga una edad superior o igual a 21 años, y menor a 70 años.

    2. Los ingresos mensuales (variable ingresos) del solitante deben ser superiores a 1500000 COP mensuales. Pueden existir excepciones si el score
    crediticio (variable score) es alto. Esta excepciones se describe a continuación
    2.1 Los ingresos mínimos no pueden ser sueriores a 1423000 COP.
    2.2 El score crediticio debe ser superior a 680 puntos
    2.3 Se deben priorizar las justificaciones (variable justificación) asociadas a estudios, tratamientos de salud, o inversión en negocios propios.
    2.4 Estas condiciones suelen aplicar a personas menores a 60 años.

    3. No suelen aprobarse solicitudes con score crediticio inferior a 600 puntos. Sin embargo, si el cliente cuenta con
    un historial puede puede considerase. Además se tienen en cuenta las siguientes excepciones.
    3.1 El score crediticio debe ser mayor a 500 puntos
    3.2 Para clientes antiguos, los ingresos deben estar alrededor de 2500000 COP
    3.3 Para clientes nuevos, los ingresos deben estar alrededor de 3000000 COP
    3.4 Se deben priorizar solicitudes de acuerdo a los siguientes niveles de justificación
        Nivel 1 (Alta prioridad): justificaciones asocidas a tratamientos de salud, estudios o inversión en negocios propios.
        Nivel 2 (Media prioridad): justificaciones asociadas a eventos especiales, compra de electrodomésticos, compra de vehículos o reparación de vivienda.
        Nivel 3 (Baja prioridad): justificaciones asociadas a viajes, vacaciones o pago de deudas.
    
    4.Las justificaciones relacionadas con viajes o vacaciones suelen no ser prioritarias, pero 
    han sido aprobadas en algunos casos según el perfi. Las excepciones se situan a continuación
    4.1 Para clientes antiguos de la fintech, los ingresos deben estar alrededor de los 2500000 COP.
    4.2 Para clientes nuevos de la fintech, los ingreso deben estar alrededor de los 3000000 COP.

    5 A los clientes nuevos se les exige más rigurosidad, pero si la región es estratégica (como Bogotá o Antioquia), se pueden 
    flexibilizar algunos criterios.

    6.Si la solicitud es para estudios o salud, debería aprobarse siempre que el cliente tenga ingresos estables. Se consideran 
    ingresos estables las siguientes condiciones
    6.1 Si el score crediticio es mayor a 500 puntos y menor a 600. Entonces
    *Para clientes antiguos de la fintech, los ingresos deben estar alrededor de los 20000000 COP.
    *Para clientes nuevos de la fintech, los ingresos deben estar alrededor de los 3000000 COP.

    6.2 Si el score crediticio es mayor a 600 puntos
    *Para clientes antiguos de la fintech, los ingresos deben estar alrededor de los 1423000 COP.
    *Para clientes nuevos de la fintech, los ingresos deben estar alrededor de los 2000000 COP.

    7 En algunos casos se ha considerado la edad como un factor limitante, especialmente en mayores de 65 años. Se proponen las siguiente
    excepciones.
    7.1 El score crediticio debe ser mayor a 500 puntos
    7.2 Para clientes antiguos de la fintech, los ingresos deben estar alrededor de los 2500000 COP.
    7.3 Para clientes nuevos de la fintech, los ingresos deben estar alrededor de los 3000000 COP.    
    </context>

    <constrain>
    Responde solamente ante solicitudes crediticias. Si los que recibes son inconsistentes no proceses la solicitud y entrega un mensaje
    explicando lo sucedido
    </constrain>

    <example>
    Ejemplo 1: Cumples con las condiciones para aprobación, en un momento te enviaremos los siguientes pasos para desembolsar tu credito

    Ejemplo 2: Lo sentimos, no cumples con las condiciones necesarias para obtener un crédito. Sin embargo te damos los siguientes consejos
    (Luego de esto entrega un par de conceptos para que la persona mejore su situación financiera. Ten en cuenta el context)
    </example>

    <format>
    Entrega la respuesta en texto
    </format>

    <tone>
    Ten un tono amable, y formal. Eres un asistente.
    </tone>
    """
)


#Funciones para los nodos

def Inicio(state: State) -> State:
    mensaje_inicial = HumanMessage(content="Estoy listo para ayudarte con tu validación de crédito")
    response = llm.invoke([mensaje_inicial])
    return {**state, "messages": [mensaje_inicial, response]}


    

def validadorEdad (state: State) -> Literal['Nodo 2', 'Nodo 3']:
    edad = state['edad']
    if 21 <= edad < 70:
        return 'Nodo 2'
    else:
        return 'Nodo 3'


def ExpertoCredito(state: State) -> State:
    # Construir mensaje con variables del state
    input_message = HumanMessage(
        content = f"""
        Información del solicitante:
        - Edad: {state['edad']}
        - Ingresos: {state['ingresos']}
        - Score crediticio: {state['score']}
        - Justificación: {state['justificación']}
        - Región: {state['region']}
        - Cliente antiguo: {state['cliente_antiguo']}
        
        Evalúa esta solicitud según las políticas indicadas.
        """
    )
    
    response = llm.invoke([politicas, input_message])
    return  {**state, "messages": [input_message, response]}

def RecomendadorCredito(state: State) -> State:
    input_message = HumanMessage(
        content = f"""
        Información del solicitante:
        - Edad: {state['edad']}
        - Ingresos: {state['ingresos']}
        - Score crediticio: {state['score']}
        - Justificación: {state['justificación']}
        - Región: {state['region']}
        - Cliente antiguo: {state['cliente_antiguo']}
        
        Evalúa esta solicitud según las políticas indicadas.
        """
    )
    response = llm.invoke([recomendaciones, input_message])
    return  {**state, "messages": [input_message,response]}



#Constructor de los nodos
builder = StateGraph(State)
builder.add_node('Nodo 1',Inicio)
builder.add_node('Nodo 2',ExpertoCredito)
builder.add_node('Nodo 3',RecomendadorCredito)


builder.add_edge(START, 'Nodo 1')
builder.add_conditional_edges('Nodo 1', validadorEdad)
builder.add_edge('Nodo 2',END)
builder.add_edge('Nodo 3',END)

CreditBot = builder.compile()