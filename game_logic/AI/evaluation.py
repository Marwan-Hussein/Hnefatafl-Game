try:
    from ..Game.constants import (
        BOARD_SIZE, EMPTY, ATTACKER, DEFENDER, CORNERS, in_bounds
    )
    from ..Game.rules import check_winner, find_king
except ImportError:
    from Game.constants import (
        BOARD_SIZE, EMPTY, ATTACKER, DEFENDER, CORNERS, in_bounds
    )
    from Game.rules import check_winner, find_king

# ── tuneable weights ───────────────────────────────────────────────────────────
W_MATERIAL_ATTACKER  =  10   # score per attacker piece still on board
W_MATERIAL_DEFENDER  =  12   # score per defender piece still on board
W_KING_DISTANCE      =  8    # reward for king being close to a corner  (defender)
W_KING_MOBILITY      =  5    # reward per open square around the king   (defender)
W_ENCIRCLEMENT       =  15   # how many attackers surround king
W_ESCORT             =  6    # reward per defender adjacent to king     (defender)

INF = 10_000


# ── helpers ───────────────────────────────────────────────────────────────────

def _count_pieces(board):
    
    attackers = defenders = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board[r][c]
            if p == ATTACKER:
                attackers += 1
            elif p == DEFENDER:
                defenders += 1
    return attackers, defenders


def _min_corner_distance(kr, kc):
    return min(abs(kr - cr) + abs(kc - cc) for cr, cc in CORNERS)


def _king_adjacency(board, kr, kc):

    att = def_ = open_ = 0
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = kr + dr, kc + dc
        if not in_bounds(nr, nc):
            continue
        p = board[nr][nc]
        if p == ATTACKER:
            att += 1
        elif p == DEFENDER:
            def_ += 1
        elif p == EMPTY:
            open_ += 1
    return att, def_, open_


def _king_mobility(board, kr, kc):
    reachable = 0
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        r, c = kr + dr, kc + dc
        while in_bounds(r, c) and board[r][c] == EMPTY:
            reachable += 1
            r += dr
            c += dc
    return reachable


# ── main scoring function ─────────────────────────────────────────────────────

def evaluate(state, player):
    board = state.board

    # ── 1. terminal check ──────────────────────────────────────────────────────
    winner = check_winner(state)
    if winner == player:
        return INF
    if winner is not None:
        return -INF

    king_pos = find_king(board)
    if king_pos is None:
        return INF if player == "attacker" else -INF

    kr, kc = king_pos

    # ── 2. material ────────────────────────────────────────────────────────────
    num_att, num_def = _count_pieces(board)

    # ── 3. king distance to corner ─────────────────────────────────────────────
    max_dist = 2 * (BOARD_SIZE - 1)
    dist = _min_corner_distance(kr, kc)
    king_distance_score = W_KING_DISTANCE * (max_dist - dist)  # high when close to corner

    # ── 4. king mobility ───────────────────────────────────────────────────────
    mobility = _king_mobility(board, kr, kc)
    king_mobility_score = W_KING_MOBILITY * mobility

    # ── 5. attacker encirclement & 6. defender escort ─────────────────────────
    att_adj, def_adj, _ = _king_adjacency(board, kr, kc)

    encirclement_score = W_ENCIRCLEMENT * att_adj
    escort_score       = W_ESCORT       * def_adj

    # ── defender's perspective ─────────────────────────────────────────────────
    defender_score = (
        king_distance_score
        + king_mobility_score
        - encirclement_score           
        + escort_score
        + W_MATERIAL_DEFENDER * num_def
        - W_MATERIAL_ATTACKER * num_att
    )

    # ── attacker's perspective ─────────────────────────────────────────────────
    attacker_score = (
        - king_distance_score
        - king_mobility_score
        + encirclement_score
        - escort_score
        + W_MATERIAL_ATTACKER * num_att
        - W_MATERIAL_DEFENDER * num_def
    )

    if player == "attacker":
        return attacker_score
    else:
        return defender_score