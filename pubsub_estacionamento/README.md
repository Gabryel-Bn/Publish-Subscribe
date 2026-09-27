# Trabalho 1 — Publish/Subscribe com gRPC

Disciplina: Sistemas Distribuídos — UFF Rio das Ostras — Prof. Alessandro Copetti

## O que é

Um broker gRPC que roteia mensagens por tópico: quem publica em um tópico,
só é recebido por quem assinou aquele tópico. Aplicação usada como
exemplo: alertas de vaga de estacionamento por zona (tópico = zona, ex.
`ZONA_A`), mas o mecanismo serve para qualquer coisa (chat, preços,
notificações etc.) — só muda o texto da mensagem.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `proto/pubsub.proto` | contrato do serviço: define as 2 RPCs e as mensagens |
| `pubsub_pb2.py`, `pubsub_pb2_grpc.py` | gerados automaticamente a partir do `.proto` (não editar) |
| `server.py` | o broker: recebe publicações e distribui para assinantes |
| `publisher.py` | publica uma mensagem em um tópico |
| `subscriber.py` | assina um tópico e fica ouvindo |

## Como rodar (3 terminais)

Instalar dependência (mesma lib que vocês já usaram no trabalho anterior):
```bash
pip install grpcio grpcio-tools
```

**Terminal 1:**
```bash
python3 server.py
```

**Terminal 2:**
```bash
python3 subscriber.py ZONA_A
```

**Terminal 3:**
```bash
python3 publisher.py ZONA_A "Vaga 12 ficou ocupada"
```

O terminal 2 vai mostrar a mensagem na hora. Para provar o isolamento por
tópico, abram um 4º terminal com `python3 subscriber.py ZONA_B` e publiquem
em `ZONA_B` — só esse assinante recebe.

## Como o código funciona

1. **`.proto`** define 2 RPCs:
   - `Publish` — unária: cliente manda, servidor responde uma vez (Ack).
   - `Subscribe` — **streaming**: cliente manda um pedido só, e o servidor
     fica mandando respostas (`stream Notificacao`) para sempre. É essa RPC
     de streaming que faz o papel do "callback" do pub/sub — o gRPC cuida
     disso sozinho, sem o cliente precisar virar servidor (diferente do
     RMI, onde isso tem que ser feito na mão).

2. **`server.py`** guarda um dicionário `topico -> lista de filas`. Cada
   assinante conectado tem sua própria fila (`queue.Queue`). Quando chega
   um `Publish`, o servidor põe a mensagem em todas as filas daquele
   tópico. O `Subscribe` fica em loop tirando da fila e mandando (`yield`)
   pro cliente — isso gera o stream.

3. **`publisher.py`** e **`subscriber.py`** são clientes gRPC comuns
   (igual ao trabalho anterior de vocês), só que um chama `Publish` e o
   outro consome o stream de `Subscribe`.

