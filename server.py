import socket 
import threading
import json
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
filename = "clientTable.json"
realFilename = os.path.join(filesFolder, filename)

# Fila com requests
requestQueue = []

# Lista com o cardapio
menuList = [(0, "Brigadeiro", 1.50),
            (1, "Bolo de Rolo", 15.00),
            (2, "Brownie", 4.00),
            (3, "Petit Gateau", 11.00),
            (4, "Palha Italiana", 4.00)]

functions._print('CINtofome: Servidor Iniciado', "OUT")

def addClient(new_client):
    new_client = {
        "name": new_client[0],
        "mesa": new_client[1],
        "socket" : new_client[2],
        "conta individual" : 0.0,
        "pedidos" : []
    }

    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data['clients'].append(new_client)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

def deleteClient(clientAddress):
    obj  = json.load(open(filename))
                                                 
    for i in len(obj["clients"]):
        if obj["clients"][i]["socket"] == clientAddress:
            obj["clients"].pop(i)
            break
                               
    open("updated-file.json", "w").write(
        json.dumps(obj, sort_keys = True, indent = 4, separators = (',', ': '))
    )

def addOrder(clientAddress, order):
    obj  = json.load(open(filename))
                                                 
    for i in len(obj["clients"]):
        if obj["clients"][i]["socket"] == clientAddress:
            obj["clients"][i]["pedidos"].append((order, menuList[order][1]))
            break

def readMessage(data):
    data = json.loads(data)
    return data[0], data[1]

def CINtofomeReceiver(serverSocket):
    global requestQueue
    
    while True:
        dataRcv, clientAddress = functions.receptor(realFilename, serverSocket)
        msgType, msgContent = readMessage(dataRcv)     
        while True:
            match msgType:
                case 0:         # CHEFIA
                    # Adiciona o cliente na tabela de clientes.
                    addClient(msgContent)
                    pass
                case 1:         # CARDAPIO
                    # Adiciona o request na fila para transmissao.
                    toSendData = json.dumps((msgType, menuList))                    # Cliente : Usar loads para transformar em lista
                    requestQueue.append((toSendData, clientAddress))
                    
                case 2:         # PEDIDO
                    # Adiciona o pedido na tabela do cliente.
                    ip, port = clientAddress
                    order = int(msgContent)
                    
                case 3:         # CONTA INDIVIDUAL
                    billValue = 0.0                                                 # Ler o valor da conta no JSON
                    toSendData = json.dumps((msgType, billValue))
                    requestQueue.append((toSendData, clientAddress))
                    
                case 4:         # CONTA DA MESA
                    # Adiciona o request na fila para transmissao.
                    billValue = 0.0                                                 # Ler o valor da conta da mesa no JSON
                    toSendData = json.dumps((msgType, billValue))
                    requestQueue.append((toSendData, clientAddress))
                    
                case 5:         # PAGAR
                    paidValue = float(msgContent)                                   # Ler o valor pago pelo cliente
                    billValueClient = 0.0
                    billValueTable = 0.0                                            # Ler o valor da conta do cliente e da mesa no JSON
                    isClientPaid = False
                    isTablePaid = False
                    if paidValue >= billValueClient and paidValue <= billValueTable:
                        pass
                    toSendData = json.dumps((msgType, (isClientPaid, isTablePaid)))
                    requestQueue.append((toSendData, clientAddress))
                    
                case 6:         # LEVANTAR DA MESA
                    ip, port = clientAddress
                    deleteClient(str(ip) + ":" + str(port))
                    requestQueue.append((toSendData, clientAddress))

def CINtofomeSender(serverSocket):
    global requestQueue
    while True:
        while not requestQueue.empty():
            data, clientAddress = requestQueue[-1]
            requestQueue.pop()
            dataSent = functions.transmissor(data, serverSocket, clientAddress)

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
    
