import socket 
import random
from socket import setdefaulttimeout
import numpy as np

packSize = 1024
readSize = packSize - 1 - 2     #seqNum e checksum
timerValue = 1.0

class RandomErrorGenerator:
    def __init__(self, faultChance):
        self.faultChance = faultChance
    
    def isLost(self):
        n = np.random.uniform(0, 1)
        if n < self.faultChance:
            return True
        else:
            return False

def calculate_checksum(data):  # Form the standard IP-suite checksum
    pos = len(data)
    if pos & 1:  # If odd...
        pos -= 1
        sum = ord(data[pos])  # Prime the sum with the odd end byte
    else:
        sum = 0

    # Main code: loop to calculate the checksum
    while pos > 0:
        pos -= 2
        sum += (ord(data[pos + 1]) << 8) + ord(data[pos])

    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)
    
    result = (~ sum) & 0xffff                       # Keep lower 16 bits
    
    result = result >> 8 | ((result & 0xff) << 8)   # Swap bytes
    return "00"


# Retorna True se o pacote estiver corrompido checando o checksum
def is_corrupt(data):
    # checksum, seq_num, new_data = decodify(data)
    # new_data = seq_num + new_data
    return False
    
# Retorna o pacote ACK para o número de sequência seq_num
def get_ack(seq_num):
    return codify(seq_num, "ACK")

def decodify(data):
    checksum = data[0:2]
    seq_num = data[2]
    data = data[3:]
    return checksum, seq_num, data

def codify(seq_num, data):
    data = str(seq_num) + data
    checksum = calculate_checksum(data)
    data = checksum + data
    return data

def transmissor(filename, clientSocket, serverAddress):
    dataSent = []
    seq_num = str(0)
    REG = RandomErrorGenerator(0.2)
    
    with open(filename, 'r') as f:
        while True:

            data = f.read(readSize)
            old_data = data
            # Codifica o pacote
            data = codify(seq_num, data)
            
            # Envia o bloco de dados para o servidor
            print("Enviando dados para o receptor...")

            isError = REG.isLost()      # Retorna TRUE, caso o pacote tenha sido perdido

            clientSocket.sendto(data.encode(), serverAddress)
            dataSent.append(data)

            if isError:                     # Se o pacote for perdido, estoura o temporizador
                print("Pacote se perdera!")
                print("data: ", data)
                socket.setdefaulttimeout(0)
            else:
                socket.setdefaulttimeout(timerValue) 
            
            # Aguarda a resposta do servidor
            while True:
                print("Aguardando resposta do receptor...")
                new_data_empty = False
                try:
                    data, address = clientSocket.recvfrom(packSize)
                    print("Recebi resposta do receptor :  {}".format(data.decode()))
                    data = data.decode()
                    checksum, new_seq_num, new_data = decodify(data)
                    if not new_data:
                        new_data_empty = True
                    if not is_corrupt(data) and new_seq_num == seq_num:  # Se o pacote não estiver corrompido e for o esperado
                        print("Pacote ACK não está corrompido e é o esperado")
                        seq_num = str((int(seq_num) + 1) % 2)
                        #socket.settimeout(None)
                        break
                except socket.timeout:
                    print("Temporizador estourou") 
                    # Reenviando a msg
                    clientSocket.sendto(data.encode(), serverAddress)                               # Se estourou o temporizador, reenvia o conteúdo
                    print("reenviando data: ", data)
                    
                    # Reseta o temporizador
                    socket.setdefaulttimeout(timerValue)

                if new_data_empty:
                    print("Pacote vazio")
                    socket.setdefaulttimeout(None)
                    break
            if not old_data:
                print("Pacote vazio do final")
                break

    print("Terminei de enviar os dados")
    return dataSent

def receptor(filename, clientSocket):
    dataRcv = []
    seq_num = str(0)
    addressRcv = None
    print('Entrei no receptor')
    with open(filename, 'w') as f:
        while True:
            # Recebe o próximo bloco de dados do servidor
            data, address = clientSocket.recvfrom(packSize)
            print("Recebi dados do transm:  {}".format(data))
            data = data.decode()
            print("Recebi dados do transmissor :  {}".format(data))
            addressRcv = address
            new_checksum, new_seq_num, new_data = decodify(data)
            if not is_corrupt(data):
                print('Pacote não está corrompido')                                # Se o pacote não estiver corrompido
                if len(dataRcv) > 0 and data == dataRcv[-1]:
                    clientSocket.sendto(get_ack(seq_num).encode(), address)

                elif new_seq_num == seq_num:  
                    print('Pacote esperado...Escrevendo no arquivo')                        # Se o pacote for o esperado, escreve no arquivo
                    f.write(new_data)
                    dataRcv.append(data)

                    clientSocket.sendto(get_ack(seq_num).encode(), address)
                    seq_num = str((int(seq_num) + 1) % 2)
                else:                                                 # Se o pacote não for o esperado, reenvia o último ACK
                    print("Pacote nao eh o esperado")
                    continue
                                                                    # Se o pacote recebido for vazio, termina a recepção
            if not new_data:
                print("Pacote vazio")
                break
    print("Terminei de receber os dados")
    return dataRcv, addressRcv


def main():
    # Testagem
    b = bytes("teste", 'ascii')
    data = "teste"
    for byte in b:
        print(f'{byte:0>8b}', end=' ')
    print("\n")
    check = bytes(calculate_checksum(data), 'ascii')
    for byte in check:
        print(f'{byte:0>8b}', end=' ')
    print("\n")
    print(codify(str(0), data))
    print(decodify(codify(str(0), data)))
    print(get_ack(str(0)))

if __name__ == "__main__":
    main()