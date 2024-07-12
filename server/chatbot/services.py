import os
from django.utils import timezone
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from .models import Conversation, Message, CustomUser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser
from .chroma_utils import get_chroma_db
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import OpenAIEmbeddings
from langchain.agents import create_tool_calling_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
import plotly.figure_factory as ff
import pandas as pd
import matplotlib.pyplot as plt
import plotly
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
from datetime import datetime
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional , List
from langchain_core.output_parsers import PydanticOutputParser

global_df = None

def get_mysql_data(query):
    try:
        # Créez une connexion MySQL
        conn = mysql.connector.connect(
            host='db',
            user='lucas',
            password='password',
            database='test_db'
        )

        # Vérifiez si la connexion est réussie
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(query)
            global_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
            return global_df
        else:
            return "Erreur de connexion à la base de données MySQL."

    except mysql.connector.Error as e:
        return f"Erreur MySQL : {e}"
    finally:
        if conn.is_connected():
            conn.close()

class SQLQuery(BaseModel):
    query: str = Field(description="SQL query to execute")

@tool(args_schema = SQLQuery)
def execute_sql(query: str) -> str:
    """Returns the result of SQL query execution"""
    print('0')
    return get_mysql_data(query)

class SQLTable(BaseModel):
    database: str = Field(description="Database name")
    table: str = Field(description="Table name")

@tool(args_schema = SQLTable)
def get_table_columns(database: str, table: str) -> str:
    """Returns list of table column names and types in JSON"""

    q = '''
    select name, type
    from system.columns
    where database = '{database}'
        and table = '{table}'
    format TabSeparatedWithNames
    '''.format(database = database, table = table)
    print('1')
    return str(get_mysql_data(q))

class SQLTableColumn(BaseModel):
    database: str = Field(description="Database name")
    table: str = Field(description="Table name")
    column: str = Field(description="Column name")
    n: Optional[int] = Field(description="Number of rows, default limit 10")

@tool(args_schema = SQLTableColumn)
def get_table_column_distr(database: str, table: str, column: str, n:int = 10) -> str:
    """Returns top n values for the column in JSON"""

    q = '''
    select {column}, count(1) as count
    from {database}.{table}
    group by 1
    order by 2 desc
    limit {n}
    format TabSeparatedWithNames
    '''.format(database = database, table = table, column = column, n = n)

    result = get_mysql_data(q)
    if isinstance(result, str):  # Si c'est une chaîne, c'est une erreur
        return result
    else:
        return str(list(result[column].values))
    
@tool()
def get_plotly_figure(plotly_code: str, dataframe_json: str, dark_mode: bool = False) -> (plotly.graph_objs.Figure, str):
    """
    **Example:**
    ```python
    fig = vn.get_plotly_figure(
        plotly_code="fig = px.bar(df, x='name', y='salary')",
        df=df
    )
    fig.show()
    ```
    Get a Plotly figure from a dataframe JSON and Plotly code, and returns both the figure and a message.

    Args:
        dataframe_json (str): The dataframe in JSON string format to use.
        plotly_code (str): The Plotly code to use.
        dark_mode (bool, optional): Whether to use dark mode for the plot. Defaults to True.

    Returns:
        A tuple containing:
        - plotly.graph_objs.Figure: The Plotly figure or None if an error occurred.
        - str: A message indicating the success or failure of the operation.
    """
    # Convert the JSON string to a DataFrame
    df = pd.read_json(dataframe_json)
    
    ldict = {"df": df, "px": px, "go": go}
    try:
        exec(plotly_code, globals(), ldict)
        fig = ldict.get("fig", None)
        if fig is None:
            return None, "Aucun graphique n'a été créé."
        
        if dark_mode:
            fig.update_layout(template="plotly_dark")
        
        return fig, "Graphique créé avec succès."
    except Exception as e:
        return None, f"Erreur lors de la création du graphique : {e}"
    
@tool()    
def get_today_date(query: str) -> str:
    """
    Useful to get the date of today.
    """
    # Getting today's date in string format
    today_date_string = datetime.now().strftime("%Y-%m-%d")
    return today_date_string

@tool()
def human_tool(input: str) -> str:
    """
    You can use this tool to ask the user for the details related to the request. 
    Always use this tool if you have follow-up questions. 
    The input should be a question for the user. 
    Be concise, polite and professional when asking the questions.
    """
    return input


def handle_user_question(user, question, conversation):
    if not question:
        raise ValueError("Question is required")
    
    # Enregistrer la question de l'utilisateur comme un message
    user_message = Message.objects.create(
        conversation=conversation,
        text=question,
        type='Human',
        created_at=timezone.now(),
        updated_at=timezone.now()
    )


    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    system_message = '''
    You are working as a product analyst for the marketing company.
    Your work is very important, since your product team makes decisions based on the data you provide. So, you are extremely accurate with the numbers you provided.
    If you're not sure about the details of the request, you don't provide the answer and ask follow-up questions to have a clear understanding.
    You are very helpful and try your best to answer the questions.
    All the data is stored in SQL Database. Here is the list of tables (in the format <database>.<table>) look the database for more information:
    - test_db.users - information about the users, one row - one user

    Table users :
    id : Identifiant unique de l'utilisateur.
    firstname, lastname, email : Informations personnelles, facultatives.
    rule_at, send_email_at, played_at : Dates auxquelles l'utilisateur a accepté le règlement, d'envoi d'email et de participation, facultatives.
    target_id : Identifiant cible de l'utilisateur, facultatif.
    end_at, optin_at : Dates de fin de participation et d'opt-in, facultatives.
    src: la source de provenance de l'utilisateur.
    ip: L'adresse IP de l'utilisateur.
    os: le système d'exploitation utilisé par l'appareil de l'utilisateur.
    device: le type d'appareil utilisé par l'utilisateur.
    browser: Ce champ indique le navigateur web utilisé par l'utilisateur.
    unlimited_gift_id : Clé étrangère vers unlimited_gifts quand l'utilisateur n'a pas gagné un gift à forte valeur.
    created_at : Horodatages de création et de mise à jour.

    Table gifts : Cadeau à forte valeur limitée
    id : Identifiant unique du cadeau.
    code, type, segment : Identiques à unlimited_gifts.
    date_to_win : Date à laquelle le cadeau peut être gagné.
    image, mention, mention_2, description, subtitle : Identiques à unlimited_gifts.
    user_id : Clé étrangère vers users.
    created_at : Horodatages de création et de mise à jour.

    Table events : Stocke les informations sur les événements de l'application que peut faire un utilisateur
    id : Identifiant unique de l'événement.
    code : Code identifiant l'événement.
    description : Description de l'événement.
    created_at : Horodatages de création et de mise à jour.
    Cette table est associée au modèle Event qui utilise la relation BelongsToMany avec le modèle User pour relier les utilisateurs aux événements.

    Table event_user : Table de relation entre les événements et les utilisateurs.
    id : Identifiant unique.
    user_id : Clé étrangère vers users.
    event_id : Clé étrangère vers events.
    created_at : Horodatages de création et de mise à jour.
    Cette table sert de table pivot dans la relation many-to-many entre les utilisateurs et les événements dans le modèle User et Event.
    '''


    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",  system_message),
            ("placeholder", "{chat_history}"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),

        ]
    )

    #Récupérer tous les messages de la conversation pour créer l'historique
    messages = Message.objects.filter(conversation=conversation).order_by('created_at')
    history = []
    for message in messages:
        if message.type == 'Human':
            history.append(HumanMessage(content=message.text))
        else:
            history.append(AIMessage(content=message.text))
    print(f"History: {history}")
    try:
        tools = [
            execute_sql,
            get_table_columns,
            get_table_column_distr,
            get_plotly_figure,
            get_today_date
        ]
        llm_with_tools = llm.bind_functions(tools)
        agent = create_tool_calling_agent(llm_with_tools, tools, prompt)
        agent_executor = AgentExecutor(tools=tools, agent=agent, verbose=True)
        result = agent_executor.invoke(
            {
                "input": question,
                "chat_history": history,
            }
        )
    except Exception as e:
        # Gérer l'exception (par exemple, journaliser l'erreur, envoyer une notification, etc.)
        print(f"An error occurred: {e}")
        # Optionnellement, vous pouvez ré-élever l'exception si vous voulez qu'elle soit traitée ailleurs
        # raise
    finally:
        # Ce bloc est exécuté que l'exception soit levée ou non
        print("Execution finished.")

    # Enregistrer la réponse de l'IA comme un message
    ai_message = Message.objects.create(
        conversation=conversation,
        text=result['output'],
        type='AI',
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    return result['output']