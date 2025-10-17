
# client.py
import msvcrt
import time
import socket
import threading

should_exit = threading.Event()
waiting_for_response = threading.Event()

def quit_listener(conn):
    while not should_exit.is_set():
        waiting_for_response.wait()  # Wait until waiting phase starts
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key.lower() != 'q':
                continue
        else:
            continue


        print("[SERVER] Quitting early...")
        try:
            conn.sendall("quit".encode())
        except:
            pass
        
        should_exit.set()
        waiting_for_response.clear()  # Stop listening until next wait phase

def main():
    HOST = '0.0.0.0'
    PORT = 65432

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"[SERVER] Waiting for connection on {HOST}:{PORT}")
def main():
    HOST = input("Enter server IP address: ")  # Use 127.0.0.1 for local test
    PORT = 65432

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print("[CLIENT] Connected to server")

    threading.Thread(target=quit_listener, args=(client_socket,), daemon=True).start()

    try:
        while not should_exit.is_set():

            # Client waits for client response
            print("[CLIENT] Waiting for server's move...")
            print("Type q to exit early")
            waiting_for_response.set()  # Start listening for quit input during wait
            try:
                data = client_socket.recv(1024).decode()
                waiting_for_response.clear()  # Stop listening after received data

                if not data:
                    print("[CLIENT] Server disconnected.")
                    should_exit.set()
                    break
                if data.lower() == "quit":
                    print("[CLIENT] Server quit.")
                    should_exit.set()
                    break
                print(f"[SERVER] Move: {data}")

            except Exception as e:
                print(f"[CLIENT] Error during recv: {e}")
                should_exit.set()
                break

            # Client sends move
            move = input("Your move (or 'quit'): ")
            if move.lower() == "quit":
                client_socket.sendall("quit".encode())
                should_exit.set()
                break
            client_socket.sendall(move.encode())

            # Client wait for server's move

            # Wait for server's move
            #print("[CLIENT] Waiting for server's move...")
            #data = client_socket.recv(1024).decode()
            #if not data:
            #    print("[CLIENT] Server disconnected.")
            #    break
            #if data.lower() == "quit":
            #    print("[CLIENT] Server ended the game.")
            #    break
            #print(f"[SERVER MOVE] {data}")

            # Client responds with a move
            #move = input("Your move (or type 'quit'): ")

            #if move.lower() == "quit":
            #    print("[CLIENT] You ended the game.")
            #    client_socket.sendall("quit".encode())
            #    break
            #client_socket.sendall(move.encode())
            
            # Server waits for client response
            #print("[SERVER] Waiting for client response...")
            #print("Type q to exit early")
            #waiting_for_response.set()  # Start listening for quit input during wait


    except Exception as e:
        print(f"[CLIENT] Error: {e}")
    finally:
        client_socket.close()
        print("[CLIENT] Connection closed.")

main()
