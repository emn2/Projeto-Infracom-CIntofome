import socket
import functions 
import os
import json

packSize = functions.packSize

IP = socket.gethostbyname(socket.gethostname())
PORT = 8000

# Cria o socket do cliente, o primeiro campo informa que a comunicacao é pelo IP e o segundo campo informa o tipo do socket (UDP)
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
filesFolder = "client files"
serverAddress = (IP, PORT)


def run_client():
    global serverAddress
    global clientSocket
    functions._print("Cliente iniciado", "OUT")
    toSendData = [0, "Teste", 0, clientSocket.getsockname()[0] + ":" + str(clientSocket.getsockname()[1])]
    print(toSendData)
    toSendData = json.dumps(toSendData)
    dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
    dataRcv, serverAddress = functions.receptor(clientSocket)
    dataRcv = json.loads(dataRcv)
    print("{}".format(dataRcv[1]))
    while True:
        option = int(input("Digite a opção desejada: "))
        match option:
            case 1:
                toSendData = [1]
                toSendData = json.dumps(toSendData)
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                dataRcv = json.loads(dataRcv)
                print("Cardápio: {}".format(dataRcv[1]))

            case 2:
                toSendData = [2]
                pedido = int(input("Digite o número do pedido: "))
                toSendData.append(pedido)
                toSendData = json.dumps(toSendData)
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                dataRcv = json.loads(dataRcv)
                print("{}".format(dataRcv[1]))

            case 3:
                toSendData = [3]
                toSendData = json.dumps(toSendData)
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                dataRcv = json.loads(dataRcv)
                print("Conta Individual: {}".format(dataRcv[1]))

            case 4:
                toSendData = [4]
                toSendData = json.dumps(toSendData)
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                dataRcv = json.loads(dataRcv)
                print("Conta da Mesa: {}".format(dataRcv[1]))

            case 5:
                toSendData = [5]
                valor = float(input("Digite o valor a ser pago: "))
                toSendData.append(valor)
                toSendData = json.dumps(toSendData)
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                dataRcv = json.loads(dataRcv)
                print("{}".format(dataRcv[1]))

            case 6:
                toSendData = [6]
                toSendData = json.dumps(toSendData)
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                dataRcv = json.loads(dataRcv)
                print("{}".format(dataRcv[1]))
run_client()
clientSocket.close()
    