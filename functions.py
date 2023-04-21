import socket 

packSize = 1024
readSize = packSize - 1 - 2     #seqNum e checksum
timerValue = 1.0

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
    checksum, seq_num, new_data = decodify(data)
    new_data = seq_num + new_data
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
    data = seq_num + data
    checksum = calculate_checksum(data)
    data = checksum + data
    return data

def transmissor(file, clientSocket, serverAddress):
    dataSent = []
    seq_num = 0
    with open(file, 'r') as f:
        while True:
            data = f.read(readSize)

            # Codifica o pacote
            data = codify(seq_num, data)

            # Envia o bloco de dados para o servidor
            clientSocket.sendto(data, serverAddress)
            dataSent.append(data)
            socket.settimeout(timerValue)

            # Aguarda a resposta do servidor
            while True: 
                try:
                    data, address = clientSocket.recvfrom(packSize)
                    checksum, new_seq_num, new_data = decodify(data)
                    if not is_corrupt(data) and new_seq_num == seq_num:  # Se o pacote não estiver corrompido e for o esperado
                        seq_num = str((int(seq_num) + 1) % 2)
                        break
                except socket.timeout:     
                    # Reenviando a msg
                    clientSocket.sendto(data, address)                               # Se estourou o temporizador, reenvia o conteúdo
                    # Reseta o temporizador
                    socket.settimeout(timerValue)

            if not data:
                break

    return dataSent

def receptor(file, clientSocket, serverAddress):
    dataRcv = []
    seq_num = 0
    with open(file, 'w') as f:
        while True:
            # Recebe o próximo bloco de dados do servidor
            data, address = clientSocket.recvfrom(packSize)
            if not is_corrupt(data):                                # Se o pacote não estiver corrompido
                new_checksum, new_seq_num, new_data = decodify(data)
                if len(dataRcv) > 0 and data == dataRcv[-1]:
                    clientSocket.sendto(get_ack(seq_num), address)

                elif new_seq_num == seq_num:                        # Se o pacote for o esperado, escreve no arquivo
                    f.write(new_data)
                    dataRcv.append(data)

                    clientSocket.sendto(get_ack(seq_num), address)
                    seq_num = str((int(seq_num) + 1) % 2)
                else:                                               # Se o pacote não for o esperado, reenvia o último ACK
                    continue
                                                                    # Se o pacote recebido for vazio, termina a recepção
            if not data:
                break

    return dataRcv


def main():
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