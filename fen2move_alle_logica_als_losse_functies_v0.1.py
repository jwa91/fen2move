columns = 'abcdefgh'  # Kolommen op een schaakbord

def split_fen(fen):
    #splitst de fen in de verschillende deeltjes
    return fen.split()

def fen_to_board(fen):
    board_part = split_fen(fen)[0]
    rows = board_part.split('/')
    board = []
    for row in rows:
        board_row = []
        for char in row:
            if char.isdigit():
                board_row.extend(['-'] * int(char))
            else:
                board_row.append(char)
        board.append(board_row)
    return board

def castling_notation (fen1, fen2):
    castling_part_FEN1 = split_fen(fen1)
    castling_part_FEN2 = split_fen(fen2)
    castling_voor = set(castling_part_FEN1[2])
    castling_na = set(castling_part_FEN2[2])
    castling_verandering = castling_voor - castling_na

    # Bepaal de positie van de witte en zwarte koning in beide FENs
    koning_wit_positie_voor = castling_part_FEN1[0].find('K')
    koning_wit_positie_na = castling_part_FEN2[0].find('K')
    koning_zwart_positie_voor = castling_part_FEN1[0].find('k')
    koning_zwart_positie_na = castling_part_FEN2[0].find('k')

    # Controleer op korte rokade voor wit
    if 'K' in castling_verandering and koning_wit_positie_na > koning_wit_positie_voor:
        return 'o-o'
    # Controleer op lange rokade voor wit
    elif 'Q' in castling_verandering and koning_wit_positie_na < koning_wit_positie_voor:
        return 'o-o-o'
    # Controleer op korte rokade voor zwart
    elif 'k' in castling_verandering and koning_zwart_positie_na > koning_zwart_positie_voor:
        return 'o-o'
    # Controleer op lange rokade voor zwart
    elif 'q' in castling_verandering and koning_zwart_positie_na < koning_zwart_positie_voor:
        return 'o-o-o'

    return None

def en_passant_notation(board1, board2):
    # En passant gebeurt alleen met pionnen, dus we checken een situatie waarbij:
    # 1. Een pion schuin heeft bewogen (m.a.w., van kolom veranderd)
    # 2. Het bestemmingsveld was leeg in het eerste bord, omdat en passant de enige situatie is waarbij dat kan.
    for i in range(8):
        for j in range(8):
            if board1[i][j].lower() == 'p' and board2[i][j] == '-':
                for di, dj in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    if 0 <= i + di < 8 and 0 <= j + dj < 8:
                        if board2[i + di][j + dj].lower() == 'p' and board1[i + di][j + dj] == '-':
                            start_col = columns[j]  # Vertaal de kolomindex naar een letter
                            end_col = columns[j + dj]  # Vertaal de bestemmingskolom naar een letter
                            end_row = 8 - (i + di)  # Vertaal de bestemmingsrij naar een nummer
                            return f"{start_col}x{end_col}{end_row}"

    return None  # Geen en passant zet gevonden


def count_changed_squares(board1, board2):
    # Het aantal gewijzigde velden bepalen, dit doen we omdat we alleen de analyse hoeven te doen voor situaties
    # waarbij dat 2, 3 of 4 is
    # 2 voor reguliere zetten
    # 3 voor en passant
    #voor latere optimalisatie
    changed_count = 0
    # Elke rij en kolom doorlopen
    for i in range(len(board1)):
        for j in range(len(board1[i])):
            if board1[i][j] != board2[i][j]:
                # Vakje is gewijzigd
                changed_count += 1

    return changed_count

def find_move_positions(board1, board2):
    start_pos, end_pos = None, None
    moved_piece, captured_piece = None, None

    # Verzamel veranderde posities
    changed_positions = []
    for i in range(8):
        for j in range(8):
            if board1[i][j] != board2[i][j]:
                changed_positions.append(((i, j), board1[i][j], board2[i][j]))

    # Verwerk de veranderingen
    if len(changed_positions) == 2:
        (pos1, piece1_before, piece1_after), (pos2, piece2_before, piece2_after) = changed_positions

        # Identificeer de start- en eindpositie
        if piece1_before != '-' and piece1_after == '-':
            start_pos = pos1
            moved_piece = piece1_before
            end_pos = pos2
        elif piece2_before != '-' and piece2_after == '-':
            start_pos = pos2
            moved_piece = piece2_before
            end_pos = pos1

        # Controleer of er een stuk is geslagen
        if board1[end_pos[0]][end_pos[1]] != '-' and board1[end_pos[0]][end_pos[1]].islower() != moved_piece.islower():
            captured_piece = board1[end_pos[0]][end_pos[1]]

    return start_pos, end_pos, moved_piece, captured_piece



def check_pawn_promotion(board1, board2, start_pos, end_pos):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    start_piece = board1[start_row][start_col]
    end_piece = board2[end_row][end_col]

    if start_piece.lower() != 'p':
        return None

    if (start_piece == 'P' and end_row == 0) or (start_piece == 'p' and end_row == 7):
        return f"={end_piece.upper()}"
    return None

def regular_moves(board1, board2):
    if count_changed_squares(board1, board2) != 2:
        return None

    start_pos, end_pos, moved_piece, _ = find_move_positions(board1, board2)
    if not start_pos or not end_pos:
        return None

    start_col = columns[start_pos[1]]
    start_row = 8 - start_pos[0]
    end_col = columns[end_pos[1]]
    end_row = 8 - end_pos[0]

    promotion = check_pawn_promotion(board1, board2, start_pos, end_pos)
    if promotion:
        return f"{start_col}{start_row}{end_col}{end_row}{promotion}"

    return f"{moved_piece}{start_col}{start_row}{end_col}{end_row}"

def regular_captures(board1, board2):
    if count_changed_squares(board1, board2) != 2:
        return None

    start_pos, end_pos, moved_piece, captured_piece = find_move_positions(board1, board2)
    if not start_pos or not end_pos or not captured_piece:
        return None

    start_col = columns[start_pos[1]]
    start_row = 8 - start_pos[0]
    end_col = columns[end_pos[1]]
    end_row = 8 - end_pos[0]

    promotion = check_pawn_promotion(board1, board2, start_pos, end_pos)
    if promotion:
        return f"{moved_piece}{start_col}x{end_col}{end_row}{promotion}"

    return f"{moved_piece}x{end_col}{end_row}"

def analyze_chess_move(fen1, fen2):
    board1 = fen_to_board(fen1)
    board2 = fen_to_board(fen2)

    # Eerst controleren we op rokade
    castling_move = castling_notation(fen1, fen2)
    if castling_move is not None:
        return castling_move

    # Dan controleren we op en passant
    en_passant_move = en_passant_notation(board1, board2)
    if en_passant_move is not None:
        return en_passant_move

    # Vervolgens controleren we op reguliere vangsten
    capture_move = regular_captures(board1, board2)
    if capture_move is not None:
        return capture_move

    # Tot slot controleren we op reguliere zetten
    regular_move = regular_moves(board1, board2)
    if regular_move is not None:
        return regular_move

    # Als geen van bovenstaande geldt, is er geen geldige zet gevonden
    return "Geen geldige zet gevonden"

# Voorbeeldgebruik
fen1 = "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
fen2 = "rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2"

board1 = fen_to_board(fen1)
board2 = fen_to_board(fen2)

# De borden afdrukken voor visualisatie

print ("aantal veranderde velden:")
print (count_changed_squares(board1,board2))

print ("en passant:")
print (en_passant_notation(board1,board2))

print ("regular captures")
print (regular_captures(board1,board2))

print ("regular moves")
print (regular_moves(board1, board2))

print ("find moves position")
print (find_move_positions(board1, board2))

print ("castling:")
print (castling_notation(fen1, fen2))


print ("analyze chess move:")
print (analyze_chess_move(fen1, fen2))
