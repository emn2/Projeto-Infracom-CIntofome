import socket 
import functions

# Definir o endereco IP e a porta do servidor
IP = socket.gethostbyname(socket.gethostname())
PORT = 8000

# Cria o socket do servidor, o primeiro campo informa que a comunicaçãoo é pelo IP e o segundo campo informa o tipo do socket (UDP)
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Associar o socket ao endereco e a porta do servidor definidos anteriormente
serverSocket.bind((IP, PORT))
print('CINtofome: Servidor Iniciado')

while True:
    
    filename = "exemplo_server.txt"
    dataRcv, clientAddress = functions.receptor(filename, serverSocket) 
    print("Arquivo recebido com sucesso!")

    dataSent = functions.transmissor(filename, serverSocket, clientAddress)

    print("dataRcv: ", dataRcv)
    print("dataSent: ", dataSent)

    for i in range(len(dataRcv)):
        if dataRcv[i] != dataSent[i]:
            print('Erro na transmissão do bloco {}'.format(i))
        else:
            print('Bloco {} enviado corretamente'.format(i))
