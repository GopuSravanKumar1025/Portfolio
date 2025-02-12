import socket

def check_tcp_connectivity(remote_host: str, remote_port: int):
    try:
        # Check connectivity to VM
        sock = socket.create_connection((remote_host, remote_port), timeout=10)
        print(f"Connection to {remote_host} on port {remote_port} successful")
        sock.close()
    except (socket.timeout, socket.error) as e:
        print(f"Connection to {remote_host} on port {remote_port} failed: {e}")
        raise e  # Re-raise the caught exception

# Example usage
check_tcp_connectivity('Ip Address', 104) ##Port number is a default port number for python
