import socket 
import random
import functions
import os

# Definir o endereco IP e a porta do servidor
IP = socket.gethostbyname(socket.gethostname())
PORT = 8000

# Cria o socket do servidor, o primeiro campo informa que a comunicaçãoo é pelo IP e o segundo campo informa o tipo do socket (UDP)
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Associar o socket ao endereco e a porta do servidor definidos anteriormente
serverSocket.bind((IP, PORT))

# Pasta com os arquivos
filesFolder = "server files"
filename = "server_version.txt"
realFilename = os.path.join(filesFolder, filename)


functions._print('CINtofome: Servidor Iniciado', "OUT")

while True:
    

    dataRcv, clientAddress = functions.receptor(realFilename, serverSocket)

    dataSent = functions.transmissor(realFilename, serverSocket, clientAddress)
    # Checa se o arquivo foi enviado corretamente
    i = 0
    
    #print("dataRcv: ", dataRcv)
    #print("dataSent: ", dataSent)

    for i in range(len(dataRcv)):
        if dataRcv[i] != dataSent[i]:
            functions._print("Erro na transmissão do bloco {}".format(i), "ERR")
        else:
            functions._print("Bloco {} enviado corretamente".format(i))
    break
