import socket

target_host = '0.0.0.0'
target_port = 9998

"""
AF_INET parameter indicates we’ll use a standard IPv4 address or hostname
SOCK_STREAM indicates that this will be a TCP client
"""
# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
client.connect((target_host, target_port))

# send some data
client.send(b"Ola")

# receive some data
response = client.recv(4096)

print(response.decode())
client.close()