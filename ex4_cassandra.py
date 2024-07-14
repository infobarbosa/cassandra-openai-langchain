from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory
from cassandra.query import SimpleStatement
import openai
import numpy
import pandas as pd


cassandra_session = None
cassandra_keyspace = "infobarbank"
model_id = "text-embedding-3-small"

def get_cassandra_session():
    
    if cassandra_session is not None:

        cluster = Cluster()
        cassandra_session = cluster.connect()
        cassandra_session.set_keyspace(keyspace)

    return cassandra_session


def cleanup():
    session = get_cassandra_session()
    session.execute(f"""DROP INDEX IF EXISTS {cassandra_keyspace}.openai_desc""")
    session.execute(f"""DROP TABLE IF EXISTS {cassandra_keyspace}.products_table""")

def create_table():
    session = get_cassandra_session()
    # Tabela de vetores
    session.execute(f"""
                    CREATE TABLE IF NOT EXISTS {cassandra_keyspace}.pessoas(
                        id int,
                        chunk_id int,
                        nome text,
                        cpf text,
                        municipio text,
                        uf text,
                        openai_embedding vector<float, 1536>,
                        PRIMARY KEY (product_id, chunk_id)
                    )"""
    )
    
    # índices na coluna de vetores
    session.execute(f"""
                    CREATE CUSTOM INDEX IF NOT EXISTS pessoas_ix 
                    ON {cassandra_keyspace}.pessoas (openai_embedding) 
                    USING 'org.apache.cassandra.index.sai.StorageAttachedIndex'
                    """
    )

def lista_pessoas():
    # Carregando os dados do arquivo CSV para o Pandas
    pessoas_df = pd.read_csv('./assets/csv/pessoas.csv', sep=';')
    pessoas_df[:4]
    return pessoas_df

def carga_de_dados():
    session = get_cassandra_session()
    pessoas_df = lista_pessoas()

    for id, row in pessoas_df.iterrows():
        full_chunk = f"{row.nome} municipio: {row.municipio} uf: {row.uf}"
    
        embedding = openai.Embedding.create(input=full_chunk, model=model_id)['data'][0]['embedding']
        
        query = SimpleStatement(
                    f"""
                    INSERT INTO {cassandra_keyspace}.pessoas
                    (id, chunk_id, nome, cpf, municipio, uf, openai_embedding)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                )
        display(row)

        session.execute(query, (row.id, chunk_id, row.nome, row.cpf, row.municipio, row.uf, embedding))

# Gerando Chunks
p = lista_pessoas()
print(p.columns)
print(p.at[ 0,"NOME" ])
chunk = p.at[ 0,"NOME" ] + " / " + p.at[0,"MUNICIPIO"]
print(f"Texto a ser usado para gerar o vetor: '{chunk}'")