
try:
    import psycopg2
    print("psycopg2 is installed")
except ImportError:
    print("psycopg2 is NOT installed")
