from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory
from cassandra.query import SimpleStatement
from langchain_openai import OpenAIEmbeddings
import openai
import numpy
import pandas as pd

cassandra_keyspace = "infobarbank"
model_id = "text-embedding-3-small"

class CassandraConnection:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connect()
        return cls._instance

    def connect(self):
        self.cluster = Cluster()
        self.session = self.cluster.connect()
        self.session.set_keyspace(cassandra_keyspace)
        print(f"Conectado! keyspaces disponíveis: {self.session.execute('SELECT * FROM system_schema.keyspaces')[0]}")
    
    def get_session(self):
        return self.session


def cleanup():
    session = CassandraConnection().get_session()
    session.execute(f"DROP TABLE IF EXISTS {cassandra_keyspace}.pessoas")

def create_table():
    session = CassandraConnection().get_session()
    # Tabela de vetores
    session.execute(f"""
                    CREATE TABLE IF NOT EXISTS {cassandra_keyspace}.pessoas(
                        id bigint,
                        chunk_id bigint,
                        nome text,
                        cpf text,
                        municipio text,
                        uf text,
                        openai_embedding vector<float, 1536>,
                        PRIMARY KEY (id, chunk_id)
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
    pessoas_df = pd.read_csv('./assets/csv/pessoas.csv', sep=';', header=1)
    pessoas_df[:4]
    return pessoas_df

def carga_de_dados():
    embeddings = OpenAIEmbeddings()
    session = CassandraConnection().get_session()
    pessoas_df = lista_pessoas()
    print(pessoas_df.info())

    for id, row in pessoas_df.iterrows():

        print(f"id: {id}, row: {row}")

        full_chunk = f"{row.iloc[2]} municipio: {row.iloc[3]} uf: {row.iloc[4]}"
        print(f"full_chunk: {full_chunk}")

        embedding = embeddings.embed_query(full_chunk)
        print(f"embedding: {embedding}")

        cql_query = f"INSERT INTO {cassandra_keyspace}.pessoas(id, chunk_id, nome, cpf, municipio, uf, openai_embedding) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        print(cql_query)
        query = SimpleStatement(cql_query)

        session.execute(query, (row.iloc[0], row.iloc[0], row.iloc[2], row.iloc[1], row.iloc[3], row.iloc[4], embedding))
        

def main():
    cleanup()
    create_table()
    carga_de_dados()

if __name__ == "__main__":
    main()
