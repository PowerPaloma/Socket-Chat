import select
import sys
from ClienteObject import client
import utils 

def me():
    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
    sys.stdout.flush()
    
 
#Preenche a mensagem com espacos em branco 
def blank_spaces(message):
  while len(message) < utils.MESSAGE_LENGTH:
    message += " "
  return message[:utils.MESSAGE_LENGTH]
  
if __name__ == "__main__":

    args = sys.argv
    if len(args) != 4:
        print utils.CLIENT_USAGE
        sys.exit()

    name = args[1]
    host = args[2]
    port = int(args[3])

    client = client(name, (host, port), '')

    try:
        client.getSocket().connect(client.getAddress())
        client.getSocket().send(name)
    except:
        print utils.CLIENT_CANNOT_CONNECT.format(host, port)
        sys.exit()

    print 'Connected to remote host. Start sending messages'
    me()

    while 1:
        socket_list = [sys.stdin, client.getSocket()]

        # Pega a lista de sockets que sao readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

        for sock in read_sockets:
            if sock == client.getSocket():
                data = sock.recv(4096)
                if not data:
                    print utils.CLIENT_SERVER_DISCONNECTED.format(port)
                    sys.exit()
                else:
                    #Escreve os dados
                    sys.stdout.write(data)
                    me()


            else:
                #Ler a mensagem, retira espacos em branco e envia 
                msg = sys.stdin.readline()
                msg = blank_spaces(msg)
                client.getSocket().send(msg)
                me()
