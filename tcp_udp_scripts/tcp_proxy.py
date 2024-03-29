import sys
import socket
import threading


# These bellow is where you can change info on the buffer between remote and local
#modify requests from remote
def request_handler(buffer):
    return buffer

#modify responses for local host
def response_handler(buffer):
    return buffer


# http://code.activestate.com/recipes/142812-hex-dumper/
def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append( b"%04X %-*s %s" % (i, length*(digits + 1), hexa,
        text) )
    print(result)


def receive_from(connection: socket.socket):
    buffer = ""

    #2s timeout
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            else:
                buffer += data
    except:
        pass

    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # receive data from the remote end if necessary
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # send it to our response handler
        remote_buffer = response_handler(remote_buffer)
        
        #if we have data to send to our local cliente, send
        if len(remote_buffer):
            print(f"[<==] Sending {len(remote_buffer)} bytes to localhost")
            client_socket.send(remote_buffer)
        
        #now loop and read from local, send to remote, send to local, repeat
    while True:
        # read local host
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print(f"[==>] Received {len(local_buffer)} bytes from localhost")
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print(f"[==>] Send to remote")
        
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print(f"[<==] Received {len(remote_buffer)} bytes from remote")
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print(f"[<==] Sent to localhost")
        
        # if no data from both sides, close connections
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print(f"[*] No more data, closing connection")
            break



def server_loop(local_host,local_port,remote_host,remote_port,receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host,local_port))
    except:
        print(f"[!!] Failed to listen on {local_host}:{local_port}")
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)
    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # print out the local connection information
        print(f"[==>] Received incoming connection from {addr[0]}:{addr[1]}")
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket,remote_host,remote_port,receive_first))
        proxy_thread.start()

def main():
# no fancy command-line parsing here
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    # setup local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    # setup remote target
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    # this tells our proxy to connect and receive data
    # before sending to the remote host
    receive_first = sys.argv[5]
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
    # now spin up our listening socket
    server_loop(local_host,local_port,remote_host,remote_port,receive_first)
    
main()