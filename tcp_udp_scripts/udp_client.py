import socket

target_host = "www.google.com"
target_port = 80

# create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send some data
client.sendto(b"AAABBBCCC", (target_host, target_port))

# receive some data
data, addr = client.recvfrom(4096)

print(data.decode())
client.close()

#precisa rodar duas instancias, uma bindada na porta alvo