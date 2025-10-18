
import threading
import socket
import time
import select

import msvcrt

listeners_should_exit = threading.Event()

input_listener_status = threading.Event()
line = []
cursor = 0

def input_listener():
    while not listeners_should_exit.is_set():
        input_listener_status.wait()
        global line
        global cursor
        line = []
        cursor = 0
        while input_listener_status.is_set():
            if len(line) != 0 and line[-1] == "\n":
                continue
            
            if not msvcrt.kbhit():
                continue

            key = msvcrt.getwch()

            if key == '\r':
                print()
                line.append('\n')
                input_listener_status.clear()
                continue
            elif key == '\b':
                if cursor > 0:
                    cursor -= 1
                    line.pop(cursor)
                    tail = ''.join(line[cursor:])
                    print('\b' + tail + ' ' + '\b' * (len(tail) + 1), end='', flush=True)
            elif key in ('\x00', '\xe0'):  # special key prefix
                key2 = msvcrt.getwch()
                if key2 == 'K':  # left arrow
                    if cursor > 0:
                        print('\b', end='', flush=True)
                        cursor -= 1
                        return line, cursor, False
                elif key2 == 'M':  # right arrow
                    if cursor < len(line):
                        print(line[cursor], end='', flush=True)
                        cursor += 1
                elif key2 == 'S':  # delete
                    if cursor < len(line):
                        line.pop(cursor)
                        # redraw rest
                        print(''.join(line[cursor:]) + ' ', end='')
                        print('\b' * (len(line) - cursor + 1), end='', flush=True)
            else:
                # insert normal character at cursor
                line.insert(cursor, key)
                
                print(''.join(line[cursor:]), end='')
                print('\b' * (len(line) - cursor - 1), end='', flush=True)
                cursor += 1
    
def main():
    HOST = input("[CLIENT] Enter server IP address: ")  # Use 127.0.0.1 for local test
    PORT = 65432

    #------Connect to server------#
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print("[CLIENT] Connected to server")


    #------Setting up async input------#
    input_listener_status.clear()

    threading.Thread(target=input_listener, args = (), daemon = True).start()


    #Game loop#
    player = "CLIENT"
    playerQuit = False
    disconected = False
    try:
        while True:

            #------Waiting for move------#
            print("[CLIENT] Type q <enter> to quit the game: ", end = "", flush = True)

            input_listener_status.set()
            while True:
                ready, _, _ = select.select([client_socket], [], [], 0.5)
                
                #------Handle client response------#
                if ready:
                    move = client_socket.recv(1024).decode().lower()

                    if move == "quit":
                        player = "SERVER"
                        playerQuit = True
                    print()
                    break
    
                #------Check for interupt------#
                if not input_listener_status.is_set():
                    move = ''.join(line).lower()
                    if len(move) != 0 and ord(move[0]) == ord("q"):
                        playerQuit = True
                        client_socket.sendall("quit".encode())
                        break
                    input_listener_status.set()

            if playerQuit:
                break

            print(f"[CLIENT] Received {move} from server")
            
            #------Making move------#
            print("[CLIENT] What is your move? ", end = "", flush = True)

            input_listener_status.set()
            while True:
                #Handle interupt
                ready, _, _ = select.select([client_socket], [], [], 0.5)
                if ready and client_socket.recv(1024).decode().lower() == "quit":
                    player = "SERVER"
                    playerQuit = True
                    print()
                    break

                #Handle move complete
                if not input_listener_status.is_set():
                    break
            
            input_listener_status.clear()
            
            if playerQuit:
                break

            #Move confirmed, send to client
            move = ''.join(line).rstrip("\n").lower()
            
            print(f"[CLIENT] Sending {move} to server")

            client_socket.sendall(move.encode())

            if move == "quit":
                playerQuit = True
                break
            
    except Exception as e:
        print(f"[CLIENT] Error: {e}")
        client_socket.sendall("quit".encode())
        disconected = True

    #------Disconection handling------#
    if playerQuit:
        print(f"[CLIENT] {player.lower().title()} quit the game.")
    
    client_socket.close()
    print("[CLIENT] Disconected from Server")
    print("[CLIENT] Connection closed")

main()
