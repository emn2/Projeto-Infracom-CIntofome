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
    # Armazena o segmento da mensagem e o endereço do cliente 
    data, clientAddress = serverSocket.recvfrom(1024)
    print('')

    filename = 'recebido_' + data.decode()
    print('{} recebido de {}'.format(filename, clientAddress))

    with open(filename, 'wb') as f:
        while True:
            # Recebe o próximo pacote de dados
            data, address = serverSocket.recvfrom(1024)

            # Convertendo os dados de bytes para string
            dataString = data.decode()
            print(f'Recebido: {data.decode()}')
            #dataInt = int(dataString)
            
            # Se o pacote recebido for vazio, termina a transmissão
            if not data:
                break
            
            # Escreve os dados no arquivo
            f.write(data)
    
    print("Arquivo recebido com sucesso!")
    serverSocket.sendto(filename.encode(), clientAddress)
    print("Iniciando retransmissão do arquivo...")
    with open(filename, 'rb') as f:        
        while True:
            # Lê o próximo bloco de dados
            data = f.read(1024)

            # Se o bloco estiver vazio termina a transmissão
            if not data:
                serverSocket.sendto(data ,clientAddress)
                break
        
            serverSocket.sendto(data, clientAddress)
    print("Arquivo retransmitido com sucesso!")
