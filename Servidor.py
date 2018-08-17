import select
import socket
import sys
from ClienteObject import client
import utils 

#envia uma mensagem para todos os clientes que estao no canal "nomeCanal"
def sendCanal(sock, message, nomeCanal):
    #se o nomeCanal for vazio significa que o cliente referente ao sock nao esta associado a nenhum canal e portanto nao pode enviar mensagens 
    if nomeCanal == "":
        sendClient(sock, utils.CLIENT_WIPE_ME  + utils.SERVER_CLIENT_NOT_IN_CHANNEL+ '\n') 
    else: 
    #caso contario, eh enviado uma msg para todos os clientes que entao no canal "nomeCanal"   
        for cliente in channels[nomeCanal]:
            if cliente.getSocket() != serverSocket and cliente.getSocket() != sock:
                try:
                    cliente.getSocket().send(message)
                except:                                  
                    channels[cliente.getChannel()].remove(cliente)
                    allSockets.remove(cliente.getSocket())
                    clientList.remove(cliente)
                    cliente.getSocket().close()
                    

#Esta funcao procura em uma lista de clientes qual estah relacionado ao socketCliente e o retorna 
def getCliente(socketClient):
    for client in clientList:
        if client.getSocket() == socketClient:
            return client
                

#Cria um canal chamado "nomeChannel"                
def createChannel(cliente, nomeChannel):
    #Verifica se o canal jah existe
    for channel in channels.keys():
        if channel == nomeChannel:
                return sendClient(cliente.getSocket(), utils.CLIENT_WIPE_ME  + utils.SERVER_CHANNEL_EXISTS.format(nomeChannel)+ '\n') 
    #caso n exista o canal eh criado            
    channels[nomeChannel] = []
    channels[nomeChannel].append(cliente) 
    #Se o cliente que deseja criar a sala jah estiver em um canal ele eh removido do canal antigo e add ao novo   
    if cliente.getChannel() != "":
        sendCanal(sock, utils.CLIENT_WIPE_ME  + utils.SERVER_CLIENT_LEFT_CHANNEL.format(getCliente(sock).getName()) + '\n', cliente.getChannel())
        channels[cliente.getChannel()].remove(cliente)
        cliente.setChannel(nomeChannel) 
    #caso contario, seu canal apenas serah setado para o novo canal     
    else:
        cliente.setChannel(nomeChannel)    
    sendClient(cliente.getSocket(), utils.CLIENT_WIPE_ME + utils.SERVER_CREATE_OK + '\n') 
    
#Um cliente se junta ao canal "nomeChannel"    
def joinChannel(cliente, nomeChannel):
    #Verifica se o cliente jah faz parte do canal o qual ele quer se juntar
    if cliente.getChannel() == nomeChannel:
        sendClient(cliente.getSocket(), utils.CLIENT_WIPE_ME  + utils.SERVER_JOIN_ALREADY_PART + '\n')
    else:    
        for channel in channels.keys():
            if channel == nomeChannel:
                channels[nomeChannel].append(cliente)
                #Se o cliente que deseja se juntar a sala jah estiver em um canal ele eh removido do canal antigo e add ao novo  
                if cliente.getChannel() != "":
                    sendCanal(sock, utils.CLIENT_WIPE_ME + utils.SERVER_CLIENT_LEFT_CHANNEL.format(cliente.getName())+ '\n', cliente.getChannel())
                    channels[cliente.getChannel()].remove(cliente)
                    cliente.setChannel(nomeChannel) 
                #caso contario, seu canal apenas serah setado para o novo canal                
                else: 
                    cliente.setChannel(nomeChannel)
                sendCanal(sock, utils.CLIENT_WIPE_ME  + utils.SERVER_CLIENT_JOINED_CHANNEL.format(cliente.getName()) + '\n', cliente.getChannel())
                return sendClient(cliente.getSocket(),utils.CLIENT_WIPE_ME + utils.SERVER_CLIENT_JOIN_CHANNEL_CLI.format(nomeChannel) + '\n') 
               
        sendClient(cliente.getSocket(), utils.CLIENT_WIPE_ME  + utils.SERVER_NO_CHANNEL_EXISTS.format(nomeChannel)+ '\n') 
    


#Lista todos os canais 
def listChannel(sock):
    if channels.keys() == []:
        return sendClient(sock, utils.CLIENT_WIPE_ME + utils.SERVER_LIST_NO_CHANNEL +'\n') 
    else:   
        for channel in channels.keys():                       
            sendClient(sock, utils.CLIENT_WIPE_ME  + channel+ '\n') 


#Um cliente serah removido no canal ou da aplicacao, caso n esteja associado a nenhum canal
def quitChannel(cliente):
    if cliente.getChannel() == "":
        print "%s desconectou-se\n" % cliente.getName() 
        allSockets.remove(cliente.getSocket())  
        clientList.remove(cliente)
        cliente.getSocket().close()  
    else:
        sendCanal(sock, utils.CLIENT_WIPE_ME + utils.SERVER_CLIENT_LEFT_CHANNEL.format(cliente.getName())+ '\n', cliente.getChannel())
        channels[cliente.getChannel()].remove(cliente)
        sendClient(cliente.getSocket(), utils.CLIENT_WIPE_ME + utils.SERVER_CLIENT_LEFT_CHANNEL_CLI + '\n')  
        cliente.setChannel("")  

    
    
 #Envia uma mesagem apenas para um cliente especifico               
def sendClient(clientSocket, msg):
    try:
        clientSocket.send(msg)
    except:        
        channels[getCliente(clientSocket).getChannel()].remove(getCliente(clientSocket))
        allSockets.remove(getCliente(clientSocket).getSocket())
        clientList.remove(getCliente(clientSocket))
        clientSocket.close()
              

if __name__ == "__main__":

    allSockets = [] #lista contendo todos os sockets conectados
    clientList = [] #lista contendo todos os clientes conectados
    args = sys.argv
    if len(args) != 2: #Verifica se os argumentos foram passados corretamente
        print utils.SERVER_PORT
        sys.exit()
        
    port = int(args[1]) 
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    serverSocket.bind(("", port))
    serverSocket.listen(10)
    
    allSockets.append(serverSocket)
    
    channels = dict() #cria um dicionario que armazena os clientes associados a um canal 
    channels['split_messages'] = [] #canal criado inicialmente para o arquivo splitCliente
    

    print utils.SERVER_START.format(port)

    while 1:
        read_sockets, write_sockets, error_sockets = select.select(allSockets, [], []) #nos diz quando ha dados para ser lido em cada um dos soquetes, bem como nos diz quando eh seguro para escrever em cada um dos soquetes.

        for sock in read_sockets:
            if sock == serverSocket:
                newSock, addr = serverSocket.accept()
                nameClient = newSock.recv(utils.MESSAGE_LENGTH) #recebe o nome do cliente
                nameClient = nameClient.strip() #remove os espacos em brancos adicionais 
                newClient = client(nameClient, addr, '') #cria um novo cliente 
                newClient.setSockete(newSock)
                allSockets.append(newSock) 
                clientList.append(newClient)               
                print nameClient + " conectou-se "


            else:
                try:
                    data = sock.recv(utils.MESSAGE_LENGTH)
                    #para receber dados do splitCliente
                    while len(data) < utils.MESSAGE_LENGTH:
                        data += sock.recv(utils.MESSAGE_LENGTH) 
                    data = data.strip()                              
                    if data:
                        #verifica se a mensagem eh de controle
                        if str(data).startswith("/"):
                            verifica = data.split()
                            if verifica[0] == "/list":                        
                                if len(verifica) != 1:                                    
                                    sendClient(sock, utils.CLIENT_WIPE_ME  + utils.SERVER_JOIN_INVALID_ARGUMENT +'\n' ) 
                                else:                               
                                    listChannel(sock) 
                           
                            elif verifica[0] == "/create": 
                                if len (verifica) == 2:
                                    createChannel(getCliente(sock), verifica[1]) 
                                else:
                                    sendClient(sock, utils.CLIENT_WIPE_ME  + utils.SERVER_CREATE_REQUIRES_ARGUMENT + '\n' ) 
                                                                                                     
                            elif verifica[0] == "/join":                          
                                if len (verifica) == 2:                                    
                                    joinChannel(getCliente(sock), verifica[1])  
                                else:
                                    sendClient(sock, utils.CLIENT_WIPE_ME  + utils.SERVER_JOIN_REQUIRES_ARGUMENT + '\n')  
                            
                            elif verifica[0] == "/quit":                          
                                if len (verifica) == 1:                                    
                                    quitChannel(getCliente(sock))  
                                else:
                                    sendClient(sock, utils.CLIENT_WIPE_ME  + utils.SERVER_JOIN_REQUIRES_ARGUMENT + '\n')                                     
                                                               
                                                                                                                               
                            else:
                                sendClient(sock, utils.CLIENT_WIPE_ME  + utils.SERVER_INVALID_CONTROL_MESSAGE.format(verifica[0])+ "\n")                                
                                                                                                                                                           
                        else:                                                
                            sendCanal(sock, utils.CLIENT_WIPE_ME  + '[' + getCliente(sock).getName() + '] ' + data + '\n', getCliente(sock).getChannel())
                            

                except:
                    sendCanal(sock, utils.CLIENT_WIPE_ME  +" %s is offline\n" % getCliente(sock).getName(), getCliente(sock).getChannel())
                    print "%s desconectou-se\n" % getCliente(sock).getName()                                        
                    channels[getCliente(sock).getChannel()].remove(getCliente(sock)) 
                    allSockets.remove(sock)  
                    clientList.remove(getCliente(sock))
                    sock.close()                                     
                    continue

    serverSocket.close()
