import os, socket, json
import random

# =================== WARNA ANSI ===================
LIGHT_RED = "\033[1;31m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def clear():
    os.system("clear")

def banner():
    print(LIGHT_RED + BOLD + r"""
████████╗██╗ ██████╗████████╗ █████╗ 
╚══██╔══╝██║██╔════╝╚══██╔══╝██╔══██╗
   ██║   ██║██║        ██║   ███████║
   ██║   ██║██║        ██║   ██╔══██║
   ██║   ██║╚██████╗   ██║   ██║  ██║
   ╚═╝   ╚═╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝
          🎮 Tic-Tac-Toe 🎮
""" + RESET)

def print_board(board):
    print()
    for i in range(3):
        row_display = []
        for j in range(3):
            cell = board[i][j]
            if cell == " ":
                row_display.append(YELLOW + str(i * 3 + j + 1) + RESET)
            elif cell == "X":
                row_display.append(LIGHT_RED + "X" + RESET)
            elif cell == "O":
                row_display.append(GREEN + "O" + RESET)
        print(" " + (YELLOW + " | " + RESET).join(row_display))
        if i < 2:
            print(CYAN + "---+---+---" + RESET)
    print()

def check_winner(board, player):
    for row in board:
        if all(cell == player for cell in row):
            return True
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)) or all(board[i][2-i] == player for i in range(3)):
        return True
    return False

def is_full(board):
    return all(cell != " " for row in board for cell in row)

# =================== NETWORK ===================
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def start_server(port=12345):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", port))
    s.listen(1)
    print(GREEN + f"📡 Tunggu Connect IP: {get_local_ip()}" + RESET)
    conn, addr = s.accept()
    print(GREEN + f"✅ Terhubung Dari {addr}" + RESET)
    return conn

def start_client(ip, port=12345):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        print(GREEN + f"✅ Berhasil Terhubung Ke {ip}:{port}" + RESET)
        return s
    except Exception as e:
        print(LIGHT_RED + f"❌ Gagal Connect: {e}" + RESET)
        return None

def send_data(conn, data):
    conn.sendall(json.dumps(data).encode())

def receive_data(conn):
    try:
        data = conn.recv(1024).decode()
        return json.loads(data)
    except:
        return None

# =================== PLAYER MOVE ===================
def player_move(board, player):
    while True:
        try:
            move = int(input(GREEN + f"Giliran {player}, Pilih Posisi (1 Sampai 9): " + RESET))
            if move < 1 or move > 9:
                print(YELLOW + "⚠️ Pilih Angka 1 Sampai 9 Saja!" + RESET)
                continue
            row, col = divmod(move - 1, 3)
            if board[row][col] == " ":
                return (row, col)
            else:
                print(YELLOW + "⚠️ Posisi Sudah Terisi, Pilih Lain" + RESET)
        except ValueError:
            print(YELLOW + "⚠️ Input Salah, Masukkan Angka." + RESET)

# =================== Super AI ===================
def minimax(board, depth, is_maximizing, ai_player, human_player):
    if check_winner(board, ai_player):
        return 1
    if check_winner(board, human_player):
        return -1
    if is_full(board):
        return 0

    if is_maximizing:
        best_score = -999
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = ai_player
                    score = minimax(board, depth + 1, False, ai_player, human_player)
                    board[i][j] = " "
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = 999
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = human_player
                    score = minimax(board, depth + 1, True, ai_player, human_player)
                    board[i][j] = " "
                    best_score = min(score, best_score)
        return best_score

def computer_move(board, player):
    print(CYAN + "🤖 Komputer Sedang Berpikir..." + RESET)
    human_player = "X" if player == "O" else "O"
    empty = [(i,j) for i in range(3) for j in range(3) if board[i][j]==" "]

    if not empty:
        return

    if random.random() < 0.01:  # 001% random
        i,j = random.choice(empty)
    else:
        best_score = -999
        best_move = None
        for i_,j_ in empty:
            board[i_][j_] = player
            score = minimax(board, 0, False, player, human_player)
            board[i_][j_] = " "
            if score > best_score:
                best_score = score
                best_move = (i_, j_)
        i,j = best_move

    board[i][j] = player

# =================== MAIN ===================
def main():
    clear()
    banner()

    mode = input(YELLOW + "Lawan (1).Teman (2).Komputer (3).Jaringan? " + RESET)
    if mode not in ["1","2","3"]:
        print(LIGHT_RED + "Input salah!" + RESET); return

    if mode=="1":  # Teman
        total_rounds = input(CYAN + "Mau Berapa Ronde? " + RESET)
        total_rounds = int(total_rounds.strip() or 1)
        score = {"O":0,"X":0,"Draw":0}

        for ronde in range(1, total_rounds+1):
            board = [[" "]*3 for _ in range(3)]
            current_player = "O"

            while True:
                clear(); banner()
                print(YELLOW + f"🔄 Ronde {ronde}/{total_rounds}" + RESET)
                print(f"Skor ➡️ O: {score['O']} | X: {score['X']} | Seri: {score['Draw']}")
                print_board(board)

                row,col = player_move(board, current_player)
                board[row][col] = current_player

                if check_winner(board,current_player):
                    clear(); banner(); print_board(board)
                    print(GREEN + f"🎉 Pemain {current_player} Menang Ronde {ronde}!" + RESET)
                    score[current_player]+=1
                    break
                elif is_full(board):
                    clear(); banner(); print_board(board)
                    print(YELLOW + f"🤝 Seri Ronde {ronde}!" + RESET)
                    score["Draw"]+=1
                    break

                current_player = "X" if current_player=="O" else "O"

        clear(); banner()
        print(GREEN + "🏆 Hasil Akhir Pertandingan 🏆" + RESET)
        print(f"O: {score['O']} | X: {score['X']} | Seri: {score['Draw']}")
        if score["O"] > score["X"]:
            print(GREEN + "🎉 Pemain O Juara!" + RESET)
        elif score["X"] > score["O"]:
            print(GREEN + "🎉 Pemain X Juara!" + RESET)
        else:
            print(YELLOW + "🤝 Pertandingan Imbang!" + RESET)

    elif mode=="2":  # Komputer
        total_rounds = input(CYAN + "Mau Berapa Ronde? " + RESET)
        total_rounds = int(total_rounds.strip() or 1)
        score = {"O":0,"X":0,"Draw":0}

        for ronde in range(1, total_rounds+1):
            board = [[" "]*3 for _ in range(3)]
            current_player = "O"

            while True:
                clear(); banner()
                print(YELLOW + f"🔄 Ronde {ronde}/{total_rounds}" + RESET)
                print(f"Skor ➡️ Kamu: {score['O']} | Komputer: {score['X']} | Seri: {score['Draw']}")
                print_board(board)

                if current_player=="O":
                    row,col = player_move(board, "O")
                    board[row][col]="O"
                else:
                    computer_move(board, "X")

                if check_winner(board,"O"):
                    clear(); banner(); print_board(board)
                    print(GREEN + f"✅ Kamu Menang Ronde {ronde}!" + RESET)
                    score["O"]+=1
                    break
                elif check_winner(board,"X"):
                    clear(); banner(); print_board(board)
                    print(LIGHT_RED + f"❌ Kamu Kalah Ronde {ronde}!" + RESET)
                    score["X"]+=1
                    break
                elif is_full(board):
                    clear(); banner(); print_board(board)
                    print(YELLOW + f"🤝 Seri Ronde {ronde}!" + RESET)
                    score["Draw"]+=1
                    break

                current_player = "X" if current_player=="O" else "O"

        clear(); banner()
        print(GREEN + "🏆 Hasil Akhir Pertandingan 🏆" + RESET)
        print(f"Kamu: {score['O']} | Komputer: {score['X']} | Seri: {score['Draw']}")
        if score["O"] > score["X"]:
            print(GREEN + "✅ Selamat, Kamu Juara! 🏆" + RESET)
        elif score["X"] > score["O"]:
            print(LIGHT_RED + "❌ Sayang, Kamu Kalah! 😭" + RESET)
        else:
            print(YELLOW + "🤝 Pertandingan Imbang!" + RESET)

    elif mode=="3":  # Jaringan
        role = input(CYAN + "Mau Jadi (1) Server Atau (2) Client? " + RESET)
        if role=="1":
            conn = start_server()
            my_symbol, opp_symbol = "O","X"
            my_turn = True
            total_rounds = input(CYAN + "Mau Berapa Ronde? " + RESET)
            total_rounds = int(total_rounds.strip() or 1)
            send_data(conn, {"total_rounds": total_rounds})
        else:
            ip = input(GREEN + "Masukkan IP Server: " + RESET)
            conn = start_client(ip)
            if conn is None: return
            my_symbol, opp_symbol = "X","O"
            my_turn = False
            data = receive_data(conn)
            if not data or "total_rounds" not in data:
                print(LIGHT_RED + "⚠️ Gagal Terima Info Ronde" + RESET)
                return
            total_rounds = data["total_rounds"]

        score = {"O":0,"X":0,"Draw":0}

        for ronde in range(1, total_rounds+1):
            board = [[" "]*3 for _ in range(3)]

            while True:
                clear(); banner()
                print(YELLOW + f"🔄 Ronde {ronde}/{total_rounds}" + RESET)
                print(f"Skor ➡️ O: {score['O']} | X: {score['X']} | Seri: {score['Draw']}")
                print_board(board)

                if check_winner(board, opp_symbol):
                    print(LIGHT_RED + f"❌ Kamu Kalah Ronde {ronde}!" + RESET)
                    score[opp_symbol]+=1
                    break
                if check_winner(board, my_symbol):
                    print(GREEN + f"🎉 Kamu Menang Ronde {ronde}!" + RESET)
                    score[my_symbol]+=1
                    break
                if is_full(board):
                    print(YELLOW + f"🤝 Seri Ronde {ronde}!" + RESET)
                    score["Draw"]+=1
                    break

                if my_turn:
                    row,col = player_move(board, my_symbol)
                    board[row][col] = my_symbol
                    send_data(conn,(row,col))
                else:
                    print(CYAN + "⏳ Tunggu Giliran Lawan..." + RESET)
                    move = receive_data(conn)
                    if move is None: 
                        print(LIGHT_RED + "⚠️ Koneksi Putus!" + RESET)
                        return
                    row,col = move
                    board[row][col] = opp_symbol

                my_turn = not my_turn

        clear(); banner()
        print(GREEN + "🏆 Hasil Akhir Pertandingan 🏆" + RESET)
        print(f"O: {score['O']} | X: {score['X']} | Seri: {score['Draw']}")
        if score[my_symbol] > score[opp_symbol]:
            print(GREEN + "🏆 Kamu Juara!" + RESET)
        elif score[opp_symbol] > score[my_symbol]:
            print(LIGHT_RED + "❌ Kamu Kalah!" + RESET)
        else:
            print(YELLOW + "🤝 Pertandingan Imbang!" + RESET)

if __name__=="__main__":
    main()