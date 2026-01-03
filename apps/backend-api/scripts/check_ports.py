import socket


def check_port(host, port):
    print(f"Checking {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((host, port))
        print(f"Port {port} is OPEN on {host}")
        return True
    except Exception as e:
        print(f"Port {port} is CLOSED on {host}: {e}")
        return False
    finally:
        s.close()

if __name__ == "__main__":
    check_port("localhost", 5434)
    check_port("127.0.0.1", 5434)
    check_port("localhost", 5432)
    check_port("127.0.0.1", 5432)
