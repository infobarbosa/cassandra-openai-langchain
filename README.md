# Langchain+OpenAI com Apache Cassandra 5.0

Author: Prof. Barbosa<br>
Contact: infobarbosa@gmail.com<br>
Github: [infobarbosa](https://github.com/infobarbosa)

Neste laboratório estamos avaliando o Apache Cassandra 5.0 como sistema de armazenamento em projetos envolvendo IA Generativa (OpenAI).

Levantei o cassandra utilizando o [docker compose](./compose.yaml), presente nesse repositório.

### Diretório `data`

Diretório que vamos usar pra armazenar os dados do Cassandra.
```
mkdir data
```

### Subindo o database
```
docker compose up -d
```

### [ALTERNATIVA] Executando o container
```
docker run --name cassandra5 -v ./data:/var/lib/cassandra -d cassandra:5.0
```

Conectando via `cqlsh`
```
docker exec -it cassandra5 cqlsh
```

```
docker exec -it cassandra5 cqlsh -e "
    CREATE KEYSPACE IF NOT EXISTS infobarbank
        WITH REPLICATION = {
            'class' : 'SimpleStrategy',
            'replication_factor': 1
        };"
```

```
docker exec -it cassandra5 cqlsh -e "DESCRIBE KEYSPACE infobarbank;"
```

```
docker exec -it cassandra5 cqlsh -e "DROP TABLE infobarbank.cliente;"
```

### Tabela de exemplo

Não vamos usá-la agora. Serve apenas para checarmos se o banco está respondendo.
```
docker exec -it cassandra5 cqlsh -e "
    CREATE TABLE IF NOT EXISTS infobarbank.cliente(
        id text PRIMARY KEY,
        cpf text,
        nome text
    );"
```

```
docker exec -it cassandra5 cqlsh -e "DESCRIBE TABLE infobarbank.cliente;"
```

### Alguns inserts
```
docker exec -it cassandra5 cqlsh -e "
insert into infobarbank.cliente(id, cpf, nome) VALUES('2b162060', '***.568.112-**', 'MARIVALDA KANAMARY');
insert into infobarbank.cliente(id, cpf, nome) VALUES('2b16242a', '***.150.512-**', 'JUCILENE MOREIRA CRUZ');
insert into infobarbank.cliente(id, cpf, nome) VALUES('2b16256a', '***.615.942-**', 'GRACIMAR BRASIL GUERRA');
insert into infobarbank.cliente(id, cpf, nome) VALUES('2b16353c', '***.264.482-**', 'ALDENORA VIANA MOREIRA');
insert into infobarbank.cliente(id, cpf, nome) VALUES('2b1636ae', '***.434.715-**', 'VERA LUCIA RODRIGUES SENA');
insert into infobarbank.cliente(id, cpf, nome) VALUES('2b16396a', '***.777.135-**', 'IVONE GLAUCIA VIANA DUTRA');
insert into infobarbank.cliente(id, cpf, nome) VALUES('2b163bcc', '***.881.955-**', 'LUCILIA ROSA LIMA PEREIRA');
insert into infobarbank.cliente(id, cpf, nome) VALUES('2b163cda', '***.580.583-**', 'FRANCISCA SANDRA FEITOSA');
insert into infobarbank.cliente(id, cpf, nome) VALUES('2b163dde', '***.655.193-**', 'BRUNA DE BRITO PAIVA');
insert into infobarbank.cliente(id, cpf, nome) VALUES('2b163ed8', '***.708.013-**', 'LUCILENE PAULO BARBOSA');"
```

```
docker exec -it cassandra5 cqlsh -e "SELECT * FROM infobarbank.cliente;"
```

### Status do cassandra
```
docker exec -it cassandra5 nodetool status
```

### Flush da memória para disco
```
docker exec -it cassandra5 nodetool flush
```
