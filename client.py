import socket
import functions 

packSize = 1024

IP = socket.gethostbyname(socket.gethostname())
PORT = 8000

#Variáveis para implementação do canal de transmissão confiável rdt3.0
seq_num = 0
ack = 0
esperarAck = 0

# Cria o socket do cliente, o primeiro campo informa que a comunicacao é pelo IP e o segundo campo informa o tipo do socket (UDP)
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

filename = input('Digite o nome do arquivo de extensão txt a ser enviado: ')

serverAddress = (IP, PORT)

# Abre o arquivo para leitura
with open(filename, 'rb') as f:
    
    # Arquivo enviado
    dataSent = functions.transmissor(filename, clientSocket, serverAddress)
    
    returnFileName = 'retorno_' + filename
    dataRcv, serverAddress = functions.receptor(returnFileName, clientSocket)

    print("dataRcv: ", dataRcv)
    print("dataSent: ", dataSent)

    for i in range(len(dataRcv)):
        if dataRcv[i] != dataSent[i]:
            print('Erro na transmissão do bloco {}'.format(i))
        else:
            print('Bloco {} enviado corretamente'.format(i))

clientSocket.close()