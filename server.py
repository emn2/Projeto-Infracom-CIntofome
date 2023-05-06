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

tableFilename = os.path.join(filesFolder, filename)

# Fila com requests
requestQueue = []
requestLock = threading.Lock()

# Lista com o Cardapio
menuList = [(0, "Brigadeiro", 1.50),
            (1, "Bolo de Rolo", 15.00),
            (2, "Brownie", 4.00),
            (3, "Petit Gateau", 11.00),
            (4, "Palha Italiana", 4.00),
            (5, "Agua Voss Sem Gas", 59.90)]

functions._print("CInToFome Server iniciado.", "OUT")
functions._print("IP: {}, PORT: {}".format(IP, PORT), "OUT")

def addClient(new_client, clientSocket):  # Adiciona cliente // testado e funcionando
    new_client = {
        "name": new_client[0],
        "mesa": new_client[1],
        "conta individual": 0.0,
        "socket" : clientSocket,
        "pedidos" : []
    }

    with open(tableFilename, 'r+') as file:
        file_data = json.load(file)
        file_data['clients'].append(new_client)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

def deleteClient(clientAddress):                # Deleta o cliente solicitado // testado e funcionando
    obj  = json.load(open(tableFilename))
                                                 
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["socket"] == clientAddress:
            obj["clients"].pop(i)
            break
                               
    open(tableFilename, "w").write(
        json.dumps(obj, sort_keys = True, indent = 4, separators = (',', ': '))
    )

def addOrder(clientAddress, order):             # Adiciona o novo pedido do cliente // testado e funcionando
    obj  = json.load(open(tableFilename))
                                                 
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["socket"] == clientAddress:
            obj["clients"][i]["pedidos"].append(order)
            obj["clients"][i]["conta individual"] += menuList[order][2]
            break

    open(tableFilename, "w").write(
        json.dumps(obj, sort_keys = True, indent = 4, separators = (',', ': '))
    )

def getClientOrders(clientAddress):             # Pega a conta individual do cliente // testado e funcionando
    obj = json.load(open(tableFilename))
    
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["socket"] == clientAddress:
            contaIndividual = obj["clients"][i]["conta individual"]
            pedidosDoCliente = obj["clients"][i]["pedidos"]
            return (contaIndividual, pedidosDoCliente)

    return (-1, [])

def getTableOrders(numberTable):                # Pega a conta da mesa   // testado e funcionando
    obj = json.load(open(tableFilename))
    
    pedidosDaMesa = []
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["mesa"] == numberTable:
            pedidosDaMesa.append((obj["clients"][i]["name"], 
                                  obj["clients"][i]["pedidos"], 
                                  obj["clients"][i]['conta individual']))
    return pedidosDaMesa

def getClientTable(clientAddress):              # Pega o numero da mesa que o cliente esta sentado // testado e funcionando
    obj = json.load(open(tableFilename))
    
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["socket"] == clientAddress:
            ClientTable = obj["clients"][i]["mesa"]
            return ClientTable

    return -1
    
def showClientBill(pedidosDoCliente, billValueClient):  # testado e funcionando
    for i in range(len(pedidosDoCliente)):
        _, name, price = menuList[pedidosDoCliente[i]]
        #busca no cardápio o preço do pedido
        print("{} => R$ {}".format(name, price))
        print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
    print("Total - R$ {}".format(billValueClient))
    print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")

def showTableBill(pedidosDaMesa):                       # testado e funcionando
    totalMesa = 0.0
    for i in range(len(pedidosDaMesa)):
        nome, pedidos, contaIndividual = pedidosDaMesa[i]
        print("| {} |".format(nome)) 
        totalPessoa = 0.0
        for j in range(len(pedidos)):
            _, item, price = menuList[pedidos[j]]
            #busca no cardápio o preço do pedido
            print("{} => R$ {}".format(item, price))
            totalPessoa += price
            
        totalMesa += contaIndividual
        print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
        print("Total - R$ {}".format(totalPessoa))
        print("Desconto - R$ {}".format(totalPessoa - contaIndividual))
        print("Total a pagar - R$ {}".format(contaIndividual))
        print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
        print()

    print("Total da mesa - R$ {}".format(totalMesa))
    print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")

def getClientBill(pedidosDoCliente):        # testado e funcionando
    total = 0.0
    for i in range(len(pedidosDoCliente)):
        price = menuList[pedidosDoCliente[i]][2]
        total += price
    return total

def getTableBill(pedidosDaMesa):            # testado e funcionando
    total = 0.0
    for i in range(len(pedidosDaMesa)):
        _, _, contaIndividual = pedidosDaMesa[i]
        total += contaIndividual
    return total

def payClientBill(clientAddress):               # testado e funcionando
    obj = json.load(open(tableFilename))
    
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["socket"] == clientAddress:
            obj["clients"][i]["pedidos"] = []
            obj["clients"][i]["conta individual"] = 0.0
            break
    
    open(tableFilename, "w").write(
        json.dumps(obj, sort_keys = True, indent = 4, separators = (',', ': '))
    )
    
def getTableSize(numberTable): # Pega a quantidade de pessoas na mesa
    obj = json.load(open(tableFilename))
    size = 0
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["mesa"] == numberTable:
            size += 1
            # itera o numero do tamanho da mesa
    return size

def applyDiscount(numberTable, clientAddress, discount): # Pega a quantidade de pessoas na mesa
    obj = json.load(open(tableFilename))
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["mesa"] == numberTable and obj["clients"][i]["socket"] != clientAddress:
            obj["clients"][i]["conta individual"] -= discount

    open(tableFilename, "w").write(
        json.dumps(obj, sort_keys = True, indent = 4, separators = (',', ': '))
    )

def readMessage(data):
    data = json.loads(data)
    return data[0], data[1:]

def CINtofomeReceiver(serverSocket):
    global requestQueue
    global requestLock
    while True:
        while len(requestQueue) != 0:
            continue
        requestLock.acquire()
        dataRcv, clientAddress = functions.receptor(serverSocket)
        msgType, msgContent = readMessage(dataRcv)  
        functions._print("Mensagem do tipo {} recebida.".format(msgType), "OUT") 
        requestLock.release()
        match msgType:
            case 0:         # CHEFIA -> OK
                
                addClient(msgContent, str(clientAddress[0]) + ":" + str(clientAddress[1]))   # Adiciona o cliente na tabela de clientes.
                toSendData = """Bem vindo ao restaurante, o que deseja fazer?\n
                              1 - Ver cardápio.\n
                              2 - Fazer pedido.\n
                              3 - Pedir conta.\n
                              4 - Pedir conta da mesa.\n
                              5 - Pagar conta.\n
                              6 - Sair da mesa.\n""" 
                toSendData = json.dumps((msgType, toSendData))       
                requestQueue.append((toSendData, clientAddress))                
            case 1:         # CARDAPIO 
                toSendData = json.dumps((msgType, menuList))                    # Cliente : Usar loads para transformar em lista
                requestQueue.append((toSendData, clientAddress))
                
            case 2:         # PEDIDO -> OK
                toSendData = "Gostaria de mais algum item? Caso sim, aperte 2 novamente"
                toSendData = json.dumps((msgType, toSendData))                   
                requestQueue.append((toSendData, clientAddress))
                ip, port = clientAddress
                order = int(msgContent[0])
                addOrder(str(ip) + ":" + str(port), order)
                
            case 3:         # CONTA INDIVIDUAL
                ip, port = clientAddress
                clientStringAddress = str(ip) + ":" + str(port)
                billValueClient, pedidosDoCliente = getClientOrders(clientStringAddress)
                toSendData = json.dumps((msgType, billValueClient))
                requestQueue.append((toSendData, clientAddress))
                
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
                paidValue = float(msgContent[0])                                   # Ler o valor pago pelo cliente

                ip, port = clientAddress
                clientStringAddress = str(ip) + ":" + str(port)
                clientTable     = getClientTable(clientStringAddress)

                billValueClient, _ = getClientOrders(clientStringAddress)
                billValueTable     = getTableBill(getTableOrders(clientTable))                 # Ler o valor da conta do cliente e da mesa no JSON
                isClientPaid       = False
                isTablePaid        = False

                if paidValue >= billValueClient:
                    isClientPaid = True                   # Enviar mensagem que a conta foi paga
                    payClientBill(clientStringAddress)    # Cliente paga somente a sua parte
                    billValueTable -= billValueClient 
                    
                paidValue -= billValueClient
                print("Sobraram {} reais".format(paidValue))
                                    
                if paidValue >= 0: 
                    tableSize = getTableSize(clientTable) - 1
                    print("tableSize = ", tableSize)
                    discount = 0.0 if tableSize == 0 else (paidValue / tableSize)
                    applyDiscount(clientTable, clientStringAddress, discount)
                    
                toSendData = json.dumps((msgType, (isClientPaid, isTablePaid)))
                requestQueue.append((toSendData, clientAddress))
                
            case 6:         # LEVANTAR DA MESA
                #tem que checar se o cliente pagou a conta antes de pedir para se levantar
                
                ip, port = clientAddress
                clientStringAddress = str(ip) + ":" + str(port)

                contaIndividual, _ = getClientOrders(clientStringAddress)

                toSendData = ""
                if contaIndividual <= 0.0:
                    deleteClient(str(ip) + ":" + str(port))
                    toSendData = "Obrigado por vir ao CINtofome!"
                else:
                    toSendData = "Pague a conta antes de sair!!"

                toSendData = json.dumps((msgType, toSendData))    
                requestQueue.append((toSendData, clientAddress))
        
    
def CINtofomeSender(serverSocket):
    global requestQueue
    global requestLock
    while True:
        while len(requestQueue) > 0:
            requestLock.acquire()
            functions._print("Enviando mensagem...", "OUT")
            data, clientAddress = requestQueue[-1]
            dataSent = functions.transmissor(data, serverSocket, clientAddress)
            requestQueue.pop()
            requestLock.release()

def startThreads():

    thread_Receiver = threading.Thread(target = CINtofomeReceiver, args = (serverSocket,))
    thread_Receiver.start()

    thread_Sender = threading.Thread(target = CINtofomeSender, args = (serverSocket,))
    thread_Sender.start()

def main():
    functions._print("Iniciando as threads...", "OUT")
    startThreads()

if __name__ == "__main__":
    main()