"""
Assinante: recebe, em tempo real, as mensagens publicadas em um tópico.

Uso: python3 subscriber.py <topico>
Exemplo: python3 subscriber.py ZONA_A
"""

import sys
import grpc
import pubsub_pb2
import pubsub_pb2_grpc


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 subscriber.py <topico>")
        sys.exit(1)

    topico = sys.argv[1]
    canal = grpc.insecure_channel("localhost:50051")
    stub = pubsub_pb2_grpc.PubSubServiceStub(canal)

    print(f"Assinando o topico '{topico}'... (Ctrl+C para sair)\n")
    for notificacao in stub.Subscribe(pubsub_pb2.SubscribeRequest(topico=topico)):
        print(f"[{notificacao.topico}] {notificacao.mensagem}")


if __name__ == "__main__":
    main()
