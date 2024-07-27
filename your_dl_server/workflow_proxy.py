import socket
import threading
import socks
import select
import os
import subprocess


# Configuration parameters
HTTP_PORT = 9070
TOR_PROXY_HOST = '127.0.0.1'
TOR_PROXY_PORT = 9050  # Change this to 9150 if your Tor proxy runs on that port


# Function to handle incoming HTTP/HTTPS requests and forward them
def handle_client(client_socket):
    try:
        request = client_socket.recv(4096)
        
        # Set up the SOCKS5 connection
        socks5_socket = socks.socksocket()
        socks5_socket.set_proxy(socks.SOCKS5, TOR_PROXY_HOST, TOR_PROXY_PORT)
        
        # Extract the first line of the request
        first_line = request.split(b'\r\n')[0].decode()
        method, path, _ = first_line.split(' ')
        
        if method == 'CONNECT':
            # HTTPS connection (method is CONNECT)
            host_port = path.split(':')
            target_host = host_port[0]
            target_port = int(host_port[1])
            
            # Connect to the target host through the Tor proxy
            socks5_socket.connect((target_host, target_port))
            
            # Inform the client that the connection is established
            client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            
            # Forward data between the client and the target server
            forward_data(client_socket, socks5_socket)
        else:
            # HTTP connection
            headers = request.split(b'\r\n')
            host_line = next(line for line in headers if line.startswith(b'Host:'))
            host = host_line.split(b' ')[1].decode()
            
            # Connect to the target host through the Tor proxy
            socks5_socket.connect((host, 80))
            
            # Send the HTTP request to the target host
            socks5_socket.send(request)
            
            # Receive the response from the target host and forward it to the client
            forward_data(client_socket, socks5_socket)
    except Exception as e:
        print(f"Exception in handle_client: {e}")
    finally:
        # Close the connections
        socks5_socket.close()
        client_socket.close()


# Function to forward data between client and target server
def forward_data(client_socket, target_socket):
    sockets = [client_socket, target_socket]
    try:
        while True:
            readable, _, _ = select.select(sockets, [], [])
            if client_socket in readable:
                data = client_socket.recv(4096)
                if not data:
                    break
                target_socket.send(data)
            if target_socket in readable:
                data = target_socket.recv(4096)
                if not data:
                    break
                client_socket.send(data)
    except ConnectionResetError:
        print("Connection reset by peer.")
    except Exception as e:
        print(f"Exception in forward_data: {e}")


# Main function to start the HTTP/HTTPS server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', HTTP_PORT))
    server.listen(5)
    print(f'Server listening on port {HTTP_PORT}...')

    while True:
        client_socket, addr = server.accept()
        print(f'Accepted connection from {addr}')
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


# start server as background task
def start_background_task():
    # Start background_task.py in the background
    print('Starting tor proxy')
    process = subprocess.Popen(['dl', 'proxy'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check if the process started successfully
    try:
        stdout, stderr = process.communicate(timeout=1)
        if process.returncode is not None and process.returncode != 0:
            print(f"Failed to start background task: {stderr.decode().strip()}")
    except subprocess.TimeoutExpired:
        print("Background task started successfully.")
        # Continue with your main program


if __name__ == '__main__':
    start_server()
