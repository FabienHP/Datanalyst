import os
from django.utils import timezone
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from .models import Conversation, Message, CustomUser
from .utils import filter_complex_metadata
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser
from .chroma_utils import get_chroma_db
from .llms import get_embedding_openai, get_openai_llm
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
    vectorstore = get_chroma_db()
    retriever = vectorstore.as_retriever()
    
    retriever_tool = create_retriever_tool(
        retriever,
        "instrument_doc_retriever",
        "Query a retriever to get information about instruments",
    )


    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are george a helpful assistant for test bench developers. use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know and ask if you need search the informations about internet. Use three sentences maximum and keep the answer concise."),
            ("placeholder", "{chat_history}"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),

        ]
    )


    os.environ["TAVILY_API_KEY"] = "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"

    tavily_tool = TavilySearchResults(max_results=3)

    #Récupérer tous les messages de la conversation pour créer l'historique
    messages = Message.objects.filter(conversation=conversation).order_by('created_at')
    history = []
    for message in messages:
        if message.type == 'Human':
            history.append(HumanMessage(content=message.text))
        else:
            history.append(AIMessage(content=message.text))
    print(f"History: {history}")

    tools = [tavily_tool, retriever_tool]
    llm_with_tools = llm.bind_functions(tools)
    agent = create_tool_calling_agent(llm_with_tools, tools,prompt)
    agent_executor = AgentExecutor(tools=tools, agent=agent, verbose=True)
    result = agent_executor.invoke(
        {
            "input": question,
            "chat_history": history,
        }
    )

    agent_executor = AgentExecutor(tools=tools, agent=agent, verbose=True)

    # Enregistrer la réponse de l'IA comme un message
    ai_message = Message.objects.create(
        conversation=conversation,
        text=result['output'],
        type='AI',
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    return result['output']
