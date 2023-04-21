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

#filename = input('Digite o nome do arquivo a ser enviado: ')
filename = 'example.txt'

serverAddress = (IP, PORT)
# Envia o nome do arquivo para o servidor
clientSocket.sendto(filename.encode(), serverAddress)

# Armazenar os dados enviados para checar se foram retornados corretamente
dataSent = []

# Abre o arquivo para leitura
with open(filename, 'rb') as f:
    
    functions.transmissor(f, clientSocket, serverAddress)
    
    # Aguarda a resposta do servidor
    data, address = clientSocket.recvfrom(1024)

    filename = data.decode()
    print('{} received from {}'.format(filename, address))
    dataRcv = []
    # Abre o arquivo para escrita
    with open('retorno_' + filename, 'wb') as f:
        while True:
            # Escreve o próximo bloco de dados no arquivo
            data, address = clientSocket.recvfrom(1024)
            
            f.write(data)
            dataRcv.append(data)
            # Recebe o próximo bloco de dados do servidor
            # Se o pacote recebido for vazio, termina a transmissão
            if not data:
                break
            
    for i in range(len(dataRcv)):
        if dataRcv[i] != dataSent[i]:
            print('Erro na transmissão do bloco {}'.format(i))
        else:
            print('Bloco {} enviado corretamente'.format(i))

clientSocket.close()
