import socket
import functions 
import os

packSize = functions.packSize

IP = socket.gethostbyname(socket.gethostname())
PORT = 8000

# Cria o socket do cliente, o primeiro campo informa que a comunicacao é pelo IP e o segundo campo informa o tipo do socket (UDP)
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
filesFolder = "client files"
serverAddress = (IP, PORT)


def run_client():
    #TODO: Alterar envio e recepção para strings
    # Envia o 0
    while True:
        option = input("Digite a opção desejada:")
        match option:
            case 1:
                toSendData = "1"
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                print("Cardápio: {}".format(dataRcv))

            case 2:
                toSendData = "2"
                pedido = input("Digite o número do pedido: ")
                toSendData = toSendData + pedido
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                print("{}".format(dataRcv))

            case 3:
                toSendData = "3"
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                print("Conta Individual: {}".format(dataRcv))

            case 4:
                toSendData = "4"
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                print("Conta da Mesa: {}".format(dataRcv))

            case 5:
                toSendData = "5"
                valor = input("Digite o valor a ser pago: ")
                toSendData = toSendData + valor
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                print("{}".format(dataRcv))

            case 6:
                toSendData = "6"
                dataSent = functions.transmissor(toSendData, clientSocket, serverAddress)
                dataRcv, serverAddress = functions.receptor(clientSocket)
                print("{}".format(dataRcv))
                break

clientSocket.close()
    