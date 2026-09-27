"""
Servidor Pub/Sub (gRPC). Roda em uma porta e faz o papel de "broker":
guarda, para cada tópico, uma fila por assinante conectado.

- Publish: recebe (topico, mensagem) e entrega para todos que assinaram esse tópico.
- Subscribe: cliente assina um tópico e recebe, via stream, tudo que for publicado nele.

Uso: python3 server.py
"""

import queue
import threading
from concurrent import futures

import grpc
import pubsub_pb2
import pubsub_pb2_grpc

PORTA = 50051


class PubSubServicer(pubsub_pb2_grpc.PubSubServiceServicer):
    def __init__(self):
        self.assinantes = {}       # topico -> lista de Queue
        self.lock = threading.Lock()

    def Publish(self, request, context):
        with self.lock:
            filas = list(self.assinantes.get(request.topico, []))

        for fila in filas:
            fila.put(request.mensagem)

        print(f"[PUBLISH] topico='{request.topico}' mensagem='{request.mensagem}' "
              f"-> {len(filas)} assinante(s)")
        return pubsub_pb2.Ack(sucesso=True)

    def Subscribe(self, request, context):
        minha_fila = queue.Queue()
        with self.lock:
            self.assinantes.setdefault(request.topico, []).append(minha_fila)
        print(f"[SUBSCRIBE] novo assinante no topico '{request.topico}'")

        try:
            while context.is_active():
                try:
                    msg = minha_fila.get(timeout=1.0)
                    yield pubsub_pb2.Notificacao(topico=request.topico, mensagem=msg)
                except queue.Empty:
                    continue
        finally:
            with self.lock:
                self.assinantes[request.topico].remove(minha_fila)
            print(f"[UNSUBSCRIBE] assinante saiu do topico '{request.topico}'")


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pubsub_pb2_grpc.add_PubSubServiceServicer_to_server(PubSubServicer(), server)
    server.add_insecure_port(f"[::]:{PORTA}")
    server.start()
    print(f"Servidor rodando na porta {PORTA}. Ctrl+C para parar.")
    server.wait_for_termination()


if __name__ == "__main__":
    main()
