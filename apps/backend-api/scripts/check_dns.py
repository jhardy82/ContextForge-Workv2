import socket


def log(msg):
    with open("dns_check.log", "a") as f:
        f.write(msg + "\n")

def check_dns(hostname):
    log(f"Resolving {hostname}...")
    try:
        ip = socket.gethostbyname(hostname)
        log(f"Success! {hostname} -> {ip}")
    except Exception as e:
        log(f"Failed to resolve {hostname}: {e}")

if __name__ == "__main__":
    with open("dns_check.log", "w") as f:
        f.write("Starting DNS Check...\n")
    check_dns("aws-1-us-west-1.pooler.supabase.com")
    check_dns("db.cwohzhbuftwssqopbxdi.supabase.co")
    check_dns("google.com")
