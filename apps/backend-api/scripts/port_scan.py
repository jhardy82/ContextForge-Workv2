import socket


def check_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
            return True
        except:
            return False

ports = [5432, 5433, 5434, 54321, 54322, 54323, 6543]
results = {}
for p in ports:
    results[p] = check_port("127.0.0.1", p)

print(f"Port scan results for 127.0.0.1: {results}")
