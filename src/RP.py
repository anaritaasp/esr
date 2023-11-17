import threading
import time
import subprocess

class RP:
    def __init__(self):
        self.servers_info = {}  # Information about the connected servers
        self.sessions = {}  # Information about active sessions
    
    def broadcast_request(self, content):
        """Broadcast a request to adjacent servers to find the specified content."""
        self.propagate_request(content, self.adjacent_servers, [])

    def propagate_request(self, content, servers_to_check, visited_servers):
        """Propagate the request to adjacent servers and collect the IP addresses of servers with the content."""
        for server in servers_to_check:
            if server not in visited_servers:
                visited_servers.append(server)
                if self.check_content(server, content):
                    print(f"Content found at server: {server}")
                    # Add the server IP to the list of servers with the content
                    # Return the list of IP addresses of servers with the content
                else:
                    # Get the adjacent servers of the current server and propagate the request
                    adjacent_servers = self.get_adjacent_servers(server)
                    self.propagate_request(content, adjacent_servers, visited_servers)

    def check_content(self, server, content):
        """Check if the specified content is available at the server."""
        # Add logic to check if the content is available at the server
        return True  # Replace with actual logic

    def create_session(self, session_id, client_info, server_ip):
        """Create a new session between client and server."""
        self.sessions[session_id] = {"client_info": client_info, "server_ip": server_ip}

    def close_session(self, session_id):
        """Close an active session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def route_data(self, session_id, data):
        # Route the data to the server with the lowest latency
        best_server = self.choose_best_server()
        print(f"Routing data to {best_server}")
        # Add logic to send data to the chosen server

    def update_server_metrics(self):
        """Regularly update the server metrics."""
        while True:
            for server_ip in self.servers_info:
                # Simulated update of metrics (replace with real metrics update logic)
                self.servers_info[server_ip]["speed"] = self.get_server_latency(server_ip)
                # Add logic to update other metrics such as availability, load, etc.
                time.sleep(1)  # Wait for a time interval before the next update

    def get_server_latency(self, server_ip):
        """Measure the latency of a certain server."""
        # Replace this function with the actual logic to measure the server latency
        # Send a test packet to the server and calculate the round-trip time
        ping_response = subprocess.Popen(["ping", "-c", "4", server_ip], stdout=subprocess.PIPE).stdout.read().decode('utf-8')
        latency = float(ping_response.split("time=")[1].split(" ms")[0])
        return latency

    # o melhor servidor terá a menor latencia e o conteudo pretendido pelo cliente
    def choose_best_server(self, requested_content):
        """Select the server with the lowest latency and requested content."""
        available_servers = [server for server, info in self.servers_info.items() if requested_content in info.get("content", [])]

        if not available_servers:
            return None  # Se não houver servidores com o conteúdo, retorna None

        # Encontra o servidor com menor latência entre os servidores disponíveis
        best_server = min(available_servers, key=lambda x: self.servers_info[x]["speed"])
        return best_server

# Initialize the continuous update of server metrics in a separate thread
rp = RP()
update_thread = threading.Thread(target=rp.update_server_metrics)
update_thread.daemon = True  # Set the thread as a daemon to stop when the main program ends
update_thread.start()