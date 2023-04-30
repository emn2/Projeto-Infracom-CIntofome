import socket
import functions 
import os

packSize = functions.packSize

IP = socket.gethostbyname(socket.gethostname())
PORT = 8000

functions._print('CINtofome: Cliente Iniciado', "OUT")

# Cria o socket do cliente, o primeiro campo informa que a comunicacao é pelo IP e o segundo campo informa o tipo do socket (UDP)
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#functions._print('Digite o nome do arquivo de extensão ".txt" a ser enviado: ', "OUT")

filename = input("[INPUT]: ")
filesFolder = "client files"
#filename = "meuArquivo.txt"
realFilename = os.path.join(filesFolder, filename)

serverAddress = (IP, PORT)

# Arquivo enviado
dataSent = functions.transmissor(realFilename, clientSocket, serverAddress)

returnFileName = 'retorno_' + filename
returnFileName = os.path.join(filesFolder, returnFileName)
dataRcv, serverAddress = functions.receptor(returnFileName, clientSocket)

#print("dataRcv: ", dataRcv)
#print("dataSent: ", dataSent)

for i in range(len(dataRcv)):
    if dataRcv[i] != dataSent[i]:
        functions._print("Erro na transmissão do bloco {}".format(i), "ERR")
    else:
        functions._print("Bloco {} enviado corretamente".format(i))

clientSocket.close()