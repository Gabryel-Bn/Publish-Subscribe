"""
Publicador: envia uma mensagem para um tópico.

Uso: python3 publisher.py <topico> "<mensagem>"
Exemplo: python3 publisher.py ZONA_A "Vaga 12 ficou ocupada"
"""

import sys
import grpc
import pubsub_pb2
import pubsub_pb2_grpc


def main():
    if len(sys.argv) != 3:
        print('Uso: python3 publisher.py <topico> "<mensagem>"')
        sys.exit(1)

    topico, mensagem = sys.argv[1], sys.argv[2]
    canal = grpc.insecure_channel("localhost:50051")
    stub = pubsub_pb2_grpc.PubSubServiceStub(canal)

    resposta = stub.Publish(pubsub_pb2.PublishRequest(topico=topico, mensagem=mensagem))
    print(f"Publicado em '{topico}': {mensagem}  (sucesso={resposta.sucesso})")


if __name__ == "__main__":
    main()
