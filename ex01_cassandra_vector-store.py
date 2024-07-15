import os
os.environ["USER_AGENT"] = "meumozila"
from cassandra.cluster import Cluster

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Cassandra
from langchain.chains import create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever

KEYSPACE_NAME = "infobarbank"

def get_documents_from_web(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, 
        chunk_overlap=20
    )
    splitDocs = splitter.split_documents(docs)
    return splitDocs

def create_db(docs):
    cluster = Cluster()
    session = cluster.connect()

    embeddings = OpenAIEmbeddings()
    vectorStore = Cassandra.from_documents(
        documents=docs, 
        embedding=embeddings,
        table_name="meuteste",
        session=session, 
        keyspace=KEYSPACE_NAME
    )
    
    return vectorStore

def create_chain(vectorStore):
    model = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.4)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's questions based on the context: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")

    ])

    chain = create_stuff_documents_chain(
        llm=model,
        prompt=prompt
    )

    retriever = vectorStore.as_retriever(search_kwargs={"k": 3})
    retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("human", "Given the context above, generate a search query to look up in order to get information relavant to de conversation")
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm=model,
        retriever=retriever,
        prompt=retriever_prompt
    )

    retrieval_chain = create_retrieval_chain(
        history_aware_retriever, 
        chain
    )

    return retrieval_chain

def process_chat(chain, question, chat_history):
    response = chain.invoke({
        "input": question,
        "chat_history": chat_history
    })

    print(type(response))

    return response["answer"]

if __name__ == "__main__":
    docs = get_documents_from_web("https://python.langchain.com/v0.1/docs/expression_language/")
    vectorStore = create_db(docs)
    chain = create_chain(vectorStore)

    chat_history = []

    user_input = None
    while True:
        user_input = input("Ask me a question: ")
        if user_input == "exit":
            break
        elif user_input == "":
            continue
        
        response = (process_chat(chain, user_input, chat_history))
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=response))

        print(f"Assistant: {response}")

