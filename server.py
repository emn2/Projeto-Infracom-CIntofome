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

# Lista com o Cardapio
menuList = [(0, "Brigadeiro", 1.50),
            (1, "Bolo de Rolo", 15.00),
            (2, "Brownie", 4.00),
            (3, "Petit Gateau", 11.00),
            (4, "Palha Italiana", 4.00),
            (5, "Agua Voss Sem Gas", 59.90)]

conversionPrice = [("Brigadeiro", 1.50), 
                   ("Bolo de Rolo", 15.00),
                   ("Brownie", 4.00),
                   ("Petit Gateau", 11.00),
                   ("Palha Italiana", 4.00),
                   ("Agua Voss Sem Gas", 59.90)]

functions._print('CINtofome: Servidor Iniciado', "OUT")

def addClient(new_client):
    new_client = {
        "name": new_client[0],
        "mesa": new_client[1],
        "socket" : new_client[2],
        "conta individual" : 0.0,
        "pedidos" : []
    }

    with open(realFilename, 'r+') as file:
        file_data = json.load(file)
        file_data['clients'].append(new_client)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

def deleteClient(clientAddress): # Deleta o cliente solicitado
    obj  = json.load(open(realFilename))
                                                 
    for i in len(obj["clients"]):
        if obj["clients"][i]["socket"] == clientAddress:
            obj["clients"].pop(i)
            break
                               
    open("updated-file.json", "w").write(
        json.dumps(obj, sort_keys = True, indent = 4, separators = (',', ': '))
    )

def addOrder(clientAddress, order):
    obj  = json.load(open(realFilename))
                                                 
    for i in len(obj["clients"]):
        if obj["clients"][i]["socket"] == clientAddress:
            obj["clients"][i]["pedidos"].append((order, menuList[order][1]))
            break

def getClientOrders(clientAddress): # Pega a conta individual do cliente
    obj = json.load(open(realFilename))
    
    for i in len(obj["clients"]):
        if obj["clients"][i]["socket"] == clientAddress:
            pedidosDoCliente = obj["clients"][i]["pedidos"]
            return pedidosDoCliente

    return []

def getTableOrders(numberTable): # Pega a conta da mesa
    obj = json.loads(open(realFilename))
    
    pedidosDaMesa = []
    for i in len(obj["clients"]):
        if obj["clients"][i]["mesa"] == numberTable:
            pedidosDaMesa.append((obj["clients"][i]["nome"], obj["clients"][i]["pedidos"]))
            
    return pedidosDaMesa

def getClientTable(clientAddress):   #Pega o numero da mesa que o cliente esta sentado
    obj = json.load(open(realFilename))
    
    for i in len(obj["clients"]):
        if obj["clients"][i]["socket"] == clientAddress:
            ClientTable = obj["clients"][i]["mesa"]
            return ClientTable

    return -1
    
def showClientBill(pedidosDoCliente, billValueClient):
    pass

def showTableBill(pedidosDaMesa):
    totalMesa = 0.0
    for i in range(len(pedidosDaMesa)):
        nome, pedidos = pedidosDaMesa[i]
        print("| {} |".format(nome)) 
        totalPessoa = 0.0
        for j in range(len(pedidos)):
            item, price = conversionPrice[pedidos[j]]
            #busca no cardápio o preço do pedido
            print("{} => R$ {}".format(item, price))
            total += price
            
        totalMesa += totalPessoa
        print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
        print("Total - R$ {}".format(totalPessoa))
        print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")

    print("Total da mesa - R$ {}".format(totalMesa))
    print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")

def getClientBill(pedidosDoCliente):
    total = 0.0
    for i in range(len(pedidosDoCliente)):
        price = conversionPrice[pedidosDoCliente[i]][1]
        total += price
    return total

def getTableBill(pedidosDaMesa):
    total = 0.0
    for i in range(len(pedidosDaMesa)):
        for j in range(len(pedidosDaMesa[i])):
            price = conversionPrice[pedidosDaMesa[i][j]][1]
            total += price
    return total

def readMessage(data):
    data = json.loads(data)
    return data[0], data[1]

def payClientBill(clientAddress):
    obj = json.load(open(realFilename))
    
    for i in len(obj["clients"]):
        if obj["clients"][i]["socket"] == clientAddress:
            obj["clients"][i]["conta individual"] = 0.0
            obj["clients"][i]["pedidos"] = []
            break
    
def CINtofomeReceiver(serverSocket):
    global requestQueue
    
    while True:
        dataRcv, clientAddress = functions.receptor(realFilename, serverSocket)
        msgType, msgContent = readMessage(dataRcv)     
        while True:
            match msgType:
                case 0:         # CHEFIA -> OK
                    addClient(msgContent)                                           # Adiciona o cliente na tabela de clientes.
                case 1:         # CARDAPIO 
                    # Adiciona o request na fila para transmissao.
                    toSendData = json.dumps((msgType, menuList))                    # Cliente : Usar loads para transformar em lista
                    requestQueue.append((toSendData, clientAddress))
                    
                case 2:         # PEDIDO -> OK
                    # Adiciona o pedido na tabela do cliente.
                    ip, port = clientAddress
                    order = int(msgContent)
                    addOrder(str(ip) + ":" + str(port), order)
                    
                case 3:         # CONTA INDIVIDUAL
                    ip, port = clientAddress
                    clientStringAddress = str(ip) + ":" + str(port)
                    pedidosDoCliente = getClientOrders(clientStringAddress)
                    billValueClient = getClientBill(pedidosDoCliente)
                    toSendData = json.dumps((msgType, billValue))
                    requestQueue.append((toSendData, clientAddress))
                    #falta criar função de descontar o valor que já foi pago por outro cliente
                    #criar função showClientBill
                    showClientBill(pedidosDoCliente, billValueClient)
                    
                case 4:         # CONTA DA MESA
                    # Adiciona o request na fila para transmissao.
                    ip, port = clientAddress
                    clientStringAddress = str(ip) + ":" + str(port)
                    clientTable = getClientTable(clientStringAddress)
                    pedidosDaMesa = getTableOrders(clientTable)           # Ler o valor da conta da mesa no JSON
                    billValue = getTableBill(pedidosDaMesa)
                    showTableBill(pedidosDaMesa)
                    toSendData = json.dumps((msgType, billValue))
                    requestQueue.append((toSendData, clientAddress))
                    
                case 5:         # PAGAR
                    paidValue = float(msgContent)                                   # Ler o valor pago pelo cliente

                    ip, port = clientAddress
                    clientStringAddress = str(ip) + ":" + str(port)
                    clientTable = getClientTable(clientStringAddress)

                    billValueClient = 0.0
                    billValueTable = 0.0                                            # Ler o valor da conta do cliente e da mesa no JSON
                    isClientPaid = False
                    isTablePaid = False
                    if paidValue >= billValueClient and paidValue <= billValueTable:
                        #tratar o excedente de alguma forma, pensamos em ter um dicionario que
                        #armazena para cada mesa quanto tem excedente, a partir dele calculamos quanto de desconto
                        #uma pessoa tem, baseado na quantidade de pessoa ainda presentes na mesa
                        pass
                    elif paidValue >= billValueTable:
                        isTablePaid = True
                    else:
                        #cliente paga somente sua parte
                        #enviar mensagem que a conta foi paga
                        payClientBill(clientStringAddress)
                        pass

                    toSendData = json.dumps((msgType, (isClientPaid, isTablePaid)))
                    requestQueue.append((toSendData, clientAddress))
                    
                case 6:         # LEVANTAR DA MESA
                    #tem que checar se o cliente pagou a conta antes de pedir para se levantar
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
    
