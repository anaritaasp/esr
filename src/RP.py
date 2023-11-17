import pickle
import socket
import threading
import time
import subprocess

class RP:
    def __init__(self):
        self.servers_info = {}  # Information about the connected servers
        self.sessions = {}  # Information about active sessions
    
    # Broadcast a request to adjacent servers to find the specified content.
    def broadcast_request(self, content):
        self.propagate_request(content, self.adjacent_servers, [])

    
    # Propagate the request to adjacent servers and collect the IP addresses of servers with the content.                
    def propagate_request(self, content, servers_to_check, visited_servers):
        servers_with_content = []  # Lista para manter os IPs dos servidores com o conteúdo
        for server in servers_to_check:
            if server not in visited_servers:
                visited_servers.append(server)
                if self.check_content(server, content):
                    print(f"Content found at server: {server}")
                    servers_with_content.append(server)  # Adiciona o IP do servidor à lista

                else:
                    adjacent_servers = self.get_adjacent_servers(server)
                    # Chama recursivamente a função e armazena os IPs dos servidores com o conteúdo na lista
                    servers_with_content += self.propagate_request(content, adjacent_servers, visited_servers)

        return servers_with_content  # Retorna a lista de IPs dos servidores com o conteúdo

    # Check if the specified content is available at the server.
    def check_content(self, server, content):
        # Add logic to check if the content is available at the server
        return True  # Replace with actual logic

    # Create a new session between client and server.
    def create_session(self, session_id, client_info, server_ip):
        self.sessions[session_id] = {"client_info": client_info, "server_ip": server_ip}

    # Close an active session.
    def close_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def route_data(self, session_id, data):
        # Route the data to the server with the lowest latency
        best_server = self.choose_best_server()
        print(f"Routing data to {best_server}")
        # Add logic to send data to the chosen server

    # Regularly update the server metrics.
    def update_server_metrics(self):
        while True:
            for server_ip in self.servers_info:
                # Simulated update of metrics (replace with real metrics update logic)
                self.servers_info[server_ip]["speed"] = self.get_server_latency(server_ip)
                # Add logic to update other metrics such as availability, load, etc.
                time.sleep(1)  # Wait for a time interval before the next update

    # Measure the latency of a certain server.
    def get_server_latency(self, server_ip):
        # Replace this function with the actual logic to measure the server latency
        # Send a test packet to the server and calculate the round-trip time
        ping_response = subprocess.Popen(["ping", "-c", "4", server_ip], stdout=subprocess.PIPE).stdout.read().decode('utf-8')
        latency = float(ping_response.split("time=")[1].split(" ms")[0])
        return latency

    # o melhor servidor terá a menor latencia e o conteudo pretendido pelo cliente
    # Select the server with the lowest latency and requested content.
    def choose_best_server(self, requested_content):
        available_servers = [server for server, info in self.servers_info.items() if requested_content in info.get("content", [])]

        if not available_servers:
            return None  # Se não houver servidores com o conteúdo, retorna None

        # Encontra o servidor com menor latência entre os servidores disponíveis
        best_server = min(available_servers, key=lambda x: self.servers_info[x]["speed"])
        return best_server
    
    # receive the request from the client and send the response back
    def handle_client_request(self, client_socket, client_addr):
        # Receive the client request
        data = client_socket.recv(1024)
        data = pickle.loads(data)
        request = data.get("request", None)
        content = data.get("content", None)
        session_id = data.get("session_id", None)

        # Handle the request
        if request == "stream":
            # Get the best server to stream the content
            best_server = self.choose_best_server(content)
            if best_server:
                # Create a new session
                self.create_session(session_id, client_addr, best_server)
                # Send the response back to the client
                response = {"error": False, "server_ip": best_server}
                client_socket.send(pickle.dumps(response))
            else:
                response = {"error": True}
                client_socket.send(pickle.dumps(response))
        elif request == "data":
            # Route the data to the server with the lowest latency
            self.route_data(session_id, data)
        elif request == "close":
            # Close the session
            self.close_session(session_id)
        else:
            response = {"error": True}
            client_socket.send(pickle.dumps(response))

    def connect_client_to_server(self, client_id, server_ip, server_port):
        # Verifica se o cliente já está conectado a algum servidor
        if client_id in self.servers:
            print("The client is already connected to a server.")
            return False

        # Conecta o cliente ao servidor
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, server_port))
            self.servers[client_id] = client_socket
            print(f"Client {client_id} conected to server {server_ip}:{server_port}")
            return True
        except socket.error as e:
            print(f"Failed connection between client {client_id} and server: {str(e)}")
            return False

    def disconnect_client(self, client_id):
        # Desconecta o cliente do servidor
        if client_id in self.servers:
            self.servers[client_id].close()
            del self.servers[client_id]
            print(f"Client {client_id} disconnected from server.")
        else:
            print(f"Client {client_id} isn't connected to any server.")
    
# Initialize the continuous update of server metrics in a separate thread
rp = RP()
update_thread = threading.Thread(target=rp.update_server_metrics)
update_thread.daemon = True  # Set the thread as a daemon to stop when the main program ends
update_thread.start()