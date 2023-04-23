import socket 
import random
import datetime
import time
from socket import setdefaulttimeout
import numpy as np

packSize = 1024
readSize = packSize - 1 - 2     #seqNum e checksum
timerValue = 0.2
failRateReceiver = 0.1
failRateSender = 0.7

class RandomErrorGenerator:
    def __init__(self, faultChance):
        self.faultChance = faultChance
    
    def isLost(self):
        n = np.random.uniform(0, 1)
        if n < self.faultChance:
            return True
        else:
            return False


# ---------------------- Funções de Print ---------------------- #
def print_helper():
    lim = 1000
    i = 0
    while True:
        yield i
        i = (i + 1) % lim

print_generator = print_helper()
def _print(msg, tp = None):
    old_msg = msg
    msg = msg[:62] + ("[..]" if len(old_msg) > 62 else "")
    msg = msg[0].upper() + msg[1:]
    print("[{}]: \t {:<63}".format(next(print_generator), msg), end = "")
    print("\t({})".format(datetime.datetime.now().strftime("%H:%M:%S")), end = " - ")
    if not tp:
        print("{:<3}".format("OK"))
    else:
        print("{:<3}".format(tp))
    #time.sleep(0.3)

# ----------------------- Checksum ----------------------------- #

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
    #print(result >> 8, result & 0xff)
   # print(bin(result >> 8), bin(result & 0xff))
    #print(bin(result))
    #return result
    #TODO
    return "00"


# ---------------------- Funções de Ajuda ---------------------- #

# Retorna True se o pacote estiver corrompido.
def is_corrupt(data):
    # TODO
    # checksum, seq_num, new_data = decodify(data)
    # new_data = seq_num + new_data
    return False

# Retorna True se o pacote for um ACK
def is_ack(data, ex_seq_num):
    checksum, seq_num, new_data = decodify(data)
    return new_data == "ACK" and seq_num == ex_seq_num

# Retorna o pacote ACK para o número de sequência seq_num
def get_ack(seq_num):
    return codify(seq_num, "ACK")

# Separa o pacote em checksum, número de sequência e dados
def decodify(data):
    checksum = data[0:2]
    seq_num = data[2]
    data = data[3:]
    return checksum, seq_num, data

# Codifica o pacote com o número de sequência e o checksum
def codify(seq_num, data):
    data = str(seq_num) + data
    checksum = calculate_checksum(data)
    data = checksum + data
    return data

# -------------------------------------------------------------- #

def transmissor(filename, clientSocket, serverAddress):
    dataSent = []
    seq_num = str(0)
    packIdx = 0
    REG = RandomErrorGenerator(failRateSender)
    print("\n")
    _print("Iniciando transmissão de {}".format(filename), "OUT")
    _print("Receptor : {}".format(serverAddress), "OUT")
    _print("--------------------------------------------", "OUT")
    clientSocket.settimeout(timerValue)
    with open(filename, 'rb') as f:
        while True:

            readData = f.read(readSize).decode()
            # Codifica o pacote
            data = codify(seq_num, readData)
            if len(data.encode()) > packSize:
                _print("Pacote nº {} muito grande! Tamanho: {}".format(packIdx, len(data)), "ERR")

            # Envia o bloco de dados para o receptor
            _print("Enviando pacote nº {} de {} bytes para o receptor...".format(packIdx, len(data.encode())))

            isError = REG.isLost()          # Retorna TRUE, caso o pacote tenha sido perdido
            if not readData:
                isError = False
            if isError:                     
                _print("Pacote nº {} se perdera!".format(packIdx), "ERR")
            else:
                clientSocket.sendto(data.encode(), serverAddress)
            dataSent.append(data)
            
            # Aguarda a resposta do receptor
            ackIdx = 0
            while True:
                
                _print("Aguardando resposta do receptor para o pacote nº {}... [{}s]".format(packIdx, timerValue))
                new_data_empty = False
                try:
                    data_ack, address = clientSocket.recvfrom(packSize)
                    _print("Recebi ACK do receptor:  {}".format(data_ack))
                    ackIdx += 1
                    data_ack = data_ack.decode()
                    checksum, new_seq_num, new_data = decodify(data_ack)
                    if not new_data:
                        _print("Pacote ACK nº {} vazio : próximo pacote será enviado".format(ackIdx))
                        #socket.settimeout(0)
                        break
                    if not is_corrupt(data_ack) and is_ack(data_ack, seq_num):  # Se o pacote não estiver corrompido e for o ACK esperado
                        _print("Pacote ACK nº {} não está corrompido e é o esperado".format(ackIdx))

                        seq_num = str((int(seq_num) + 1) % 2)
                        #socket.settimeout(None)
                        break
                    else:
                        _print("Pacote ACK {} está corrompido ou não é o esperado".format(ackIdx), "ERR")
                except socket.timeout:
                    _print("Temporizador estourado! Reenviando pacote nº {}...".format(packIdx), "ERR")
                    isError = REG.isLost()          # Retorna TRUE, caso o pacote tenha sido perdido
                    if not readData:
                        isError = False
                    if isError:                     
                        _print("Reenvio do pacote nº {} se perdera!".format(packIdx), "ERR")
                    else:
                        clientSocket.sendto(data.encode(), serverAddress)   # Se estourou o temporizador, reenvia o conteúdo
                                                
            _print("............................................", "OUT")
            packIdx += 1
            if not readData:
                break

    _print("Transmissão Finalizada! {} pacotes => {} bytes enviados.".format(packIdx, sum([len(s) for s in dataSent])), "OUT")
    _print("--------------------------------------------", "OUT")
    return dataSent

def receptor(filename, clientSocket):
    dataRcv = []
    seq_num = str(0)
    addressRcv = None
    packIdx = 0
    REG = RandomErrorGenerator(failRateReceiver)

    print("\n")
    _print("Iniciando recepção de {}".format(filename), "OUT")
    _print("Receptor : {}".format(clientSocket.getsockname()), "OUT")
    _print("--------------------------------------------", "OUT")

    
    clientSocket.settimeout(None)
    with open(filename, 'w') as f:
        while True:
            # Recebe o próximo bloco de dados do servidor
            data, address = clientSocket.recvfrom(packSize)
            _print("Recebido o pacote nº {} de {} bytes do transmissor".format(packIdx, len(data)))
            
            data = data.decode()
            addressRcv = address
            new_checksum, new_seq_num, new_data = decodify(data)
            isError = REG.isLost()          # Retorna TRUE, caso o pacote tenha sido perdido
            if not new_data:
                isError = False
            if not is_corrupt(data):
                _print("Pacote nº {} não está corrompido".format(packIdx))
                if len(dataRcv) > 0 and data == dataRcv[-1]:
                    _print("Pacote nº {} é um pacote duplicado. Reenviando...".format(packIdx), "ERR")
                    
                    if isError:                     # Se o pacote for perdido, estoura o temporizador
                        _print("ACK para o pacote duplicado nº {} se perdera!".format(packIdx), "ERR")
                    else:
                        clientSocket.sendto(get_ack(new_seq_num).encode(), address)
                    packIdx -= 1

                elif new_seq_num == seq_num:  
                    _print("Pacote nº {} é o esperado. Escrevendo no arquivo...".format(packIdx))
                    f.write(new_data)
                    dataRcv.append(data)
                    if isError:                     # Se o pacote for perdido, estoura o temporizador
                        _print("ACK para o pacote nº {} se perdera!".format(packIdx), "ERR")
                    else:
                        clientSocket.sendto(get_ack(seq_num).encode(), address)
                    seq_num = str((int(seq_num) + 1) % 2)
                else:                                               # Se o pacote não for o esperado, reenvia o último ACK
                    _print("Pacote nº {} não é o esperado : EXP: {} != RCV : {}.".format(packIdx, seq_num, new_seq_num), "ERR")
                                                                    # Se o pacote recebido for vazio, termina a recepção
            packIdx += 1
            _print("............................................", "OUT")
            if not new_data:
                break
    _print("Recepção Finalizada! {} pacotes => {} bytes recebidos.".format(packIdx, sum([len(s) for s in dataRcv])), "OUT")
    _print("--------------------------------------------", "OUT")
    return dataRcv, addressRcv


def main():
    # Testagem
    b = "adsadsa".encode()
    for byte in b:
        print(f'{byte:0>8b}', end=' ')
    print("\n")
    check = calculate_checksum(b.decode()).encode()
    for byte in check:
        print(f'{byte:0>8b}', end=' ')
    print("\n")
    #print(codify(str(0), b.decode()))
    #print(decodify(codify(str(0), b.decode())))
    #print(get_ack(str(0)))

if __name__ == "__main__":
    main()