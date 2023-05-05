import json
import os

filesFolder = "server files"
filename = "clientTable.json"

realFilename = os.path.join(filesFolder, filename)

menuList = [(0, "Brigadeiro", 1.50),
            (1, "Bolo de Rolo", 15.00),
            (2, "Brownie", 4.00),
            (3, "Petit Gateau", 11.00),
            (4, "Palha Italiana", 4.00),
            (5, "Agua Voss Sem Gas", 59.90)]


def showClientBill(pedidosDoCliente, billValueClient):
    for i in range(len(pedidosDoCliente)):
        _, name, price = menuList[pedidosDoCliente[i]]
        #busca no cardápio o preço do pedido
        print("{} => R$ {}".format(name, price))
        print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
    print("Total - R$ {}".format(billValueClient))
    print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")

def getClientBill(pedidosDoCliente):
    total = 0.0
    for i in range(len(pedidosDoCliente)):
        price = menuList[pedidosDoCliente[i]][2]
        total += price
    return total


def addClient(new_client):  # Adiciona cliente // testado e funcionando
    new_client = {
        "name": new_client[0],
        "mesa": new_client[1],
        "socket" : new_client[2],
        "pedidos" : []
    }

    with open(realFilename, 'r+') as file:
        file_data = json.load(file)
        file_data['clients'].append(new_client)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

def getTableBill(pedidosDaMesa):
    total = 0.0
    for i in range(len(pedidosDaMesa)):
        name, pedidos = pedidosDaMesa[i]
        for j in range(len(pedidos)):
            price = menuList[pedidos[j]][2]
            total += price
    return total

def showTableBill(pedidosDaMesa):
    totalMesa = 0.0
    for i in range(len(pedidosDaMesa)):
        nome, pedidos = pedidosDaMesa[i]
        print("| {} |".format(nome)) 
        totalPessoa = 0.0
        for j in range(len(pedidos)):
            _, item, price = menuList[pedidos[j]]
            #busca no cardápio o preço do pedido
            print("{} => R$ {}".format(item, price))
            totalPessoa += price
            
        totalMesa += totalPessoa
        print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
        print("Total - R$ {}".format(totalPessoa))
        print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
        print()

    print("Total da mesa - R$ {}".format(totalMesa))
    print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")

def getClientOrders(clientAddress): # Pega a conta individual do cliente // testado e funcionand
    obj = json.load(open(realFilename))
    
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["socket"] == clientAddress:
            pedidosDoCliente = obj["clients"][i]["pedidos"]
            return pedidosDoCliente

    return []

def getTableOrders(numberTable): # Pega a conta da mesa
    obj = json.load(open(realFilename))
    
    pedidosDaMesa = []
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["mesa"] == numberTable:
            pedidosDaMesa.append((obj["clients"][i]["name"], obj["clients"][i]["pedidos"]))
            
    return pedidosDaMesa

def getClientTable(clientAddress):   #Pega o numero da mesa que o cliente esta sentado
    obj = json.load(open(realFilename))
    
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["socket"] == clientAddress:
            ClientTable = obj["clients"][i]["mesa"]
            return ClientTable

    return -1

def payClientBill(clientAddress):
    obj = json.load(open(realFilename))
    
    for i in range(len(obj["clients"])):
        if obj["clients"][i]["socket"] == clientAddress:
            obj["clients"][i]["pedidos"] = []
            break
    
    open(realFilename, "w").write(
        json.dumps(obj, sort_keys = True, indent = 4, separators = (',', ': '))
    )

if __name__ == '__main__':
    socket = "128.65.27.104:5000"
    # pedidosDoCliente = getClientOrders(socket)
    # totalCliente = getClientBill(pedidosDoCliente)
    # showClientBill(pedidosDoCliente, totalCliente)

    # name1 = 'Lucas'
    # socket1 = "128.65.27.104:5001"
    # mesa1 = 8
    # info1 = (name1, mesa1, socket1)

    # name2 = 'Arthur'
    # socket2 = "128.65.27.104:5002"
    # mesa2 = 8
    # info2 = (name2, mesa2, socket2)

    # addClient(info1)
    # addClient(info2)

    # pedidosDaMesa = getTableOrders(8)
    # showTableBill(pedidosDaMesa)

