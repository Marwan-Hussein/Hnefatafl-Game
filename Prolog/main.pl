%%  Pieces:                                                              
%%    a = attacker (black)                                           
%%    d = defender (white)      
%%    k = king                                                
%%    e = empty                                                       

:- use_module(library(lists)).
initial_board([
  [e, e, a, a, a, a, a, e, e],   
  [e, e, e, e, a, e, e, e, e],  
  [a, e, e, e, d, e, e, e, a], 
  [a, e, e, d, d, d, e, e, a],   
  [a, a, d, d, k, d, d, a, a],  
  [a, e, e, d, d, d, e, e, a],  
  [a, e, e, e, d, e, e, e, a],  
  [e, e, e, e, a, e, e, e, e],   
  [e, e, a, a, a, a, a, e, e]   
]).

%%  Corners
corner(1,1). corner(1,9). corner(9,1). corner(9,9).

%%  Throne
throne(5,5).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%   BOARD ACCESS AND UPDATE                                           
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

get_cell(Board, R, C, Piece) :-
    nth1(R, Board, Row),
    nth1(C, Row, Piece).

set_cell(Board, R, C, Piece, NewBoard) :-
    nth1(R, Board, OldRow),
    replace_nth(C, OldRow, Piece, NewRow),
    replace_nth(R, Board, NewRow, NewBoard).

replace_nth(1, [_|T], E, [E|T]).
replace_nth(N, [H|T], E, [H|T2]) :-
    N > 1,
    N1 is N - 1,
    replace_nth(N1, T, E, T2).

move_piece(Board, R1, C1, R2, C2, Board2) :-
    get_cell(Board, R1, C1, Piece),
    set_cell(Board, R1, C1, e, Board1),
    set_cell(Board1, R2, C2, Piece, Board2).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%   PIECE CLASSIFICATION                                              
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

is_attacker(a).
is_defender(d).
is_defender(k).
is_king(k).

side_piece(attacker, a).
side_piece(defender, d).
side_piece(defender, k).

other_side(attacker, defender).
other_side(defender, attacker).

belongs_to(a, attacker).
belongs_to(d, defender).
belongs_to(k, defender).

hostile_to_king(Board, R, C) :-
    get_cell(Board, R, C, a), !.
hostile_to_king(_, R, C) :-
    throne(R, C), !.
hostile_to_king(_, R, C) :-
    corner(R, C).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%   MOVE GENERATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

generate_rook_move(Board, R1, C1, IsKing, R2, C2) :-
    member(DR-DC, [(-1)-0, 1-0, 0-(-1), 0-1]),
    slide(Board, R1, C1, DR, DC, IsKing, R2, C2).

slide(Board, R, C, DR, DC, IsKing, R2, C2) :-
    R1 is R + DR,
    C1 is C + DC,
    R1 >= 1, R1 =< 9,
    C1 >= 1, C1 =< 9,
    get_cell(Board, R1, C1, e),
    can_stop(R1, C1, IsKing),
    R2 = R1, C2 = C1.
slide(Board, R, C, DR, DC, IsKing, R2, C2) :-
    R1 is R + DR,
    C1 is C + DC,
    R1 >= 1, R1 =< 9,
    C1 >= 1, C1 =< 9,
    get_cell(Board, R1, C1, e),
    slide(Board, R1, C1, DR, DC, IsKing, R2, C2).

can_stop(R, C, no) :- \+ throne(R,C), \+ corner(R,C).
can_stop(_, _, yes).

%%  all_moves/3

all_moves(Board, Side, AllMoves) :-
    get_cell_piece(Board, Side, Pieces),
    findall(move(R1,C1,R2,C2),
            (   member(R1-C1-P, Pieces),
                (is_king(P) -> IsKing = yes ; IsKing = no),
                generate_rook_move(Board, R1, C1, IsKing, R2, C2)
            ),
            AllMoves0),
    sort(AllMoves0, AllMoves).

%%  Collect all (Row-Col-Piece) triples belonging to Side
get_cell_piece(Board, Side, Pieces) :-
    findall(R-C-P,
            (   between(1,9,R), between(1,9,C),
                get_cell(Board, R, C, P),
                belongs_to(P, Side)
            ),
            Pieces).


would_be_sandwiched(Board, R1, C1, R2, C2, Side) :-
    %% Temporarily place piece at destination on a scratch board
    get_cell(Board, R1, C1, P),
    set_cell(Board,  R1, C1, e,  B1),
    set_cell(B1,     R2, C2, P,  B2),
    other_side(Side, Enemy),
    %% Check horizontal axis
    member(DC-DR, [1-0, 0-1]),   % one axis at a time
    Jaw1R is R2 + DR,  Jaw1C is C2 + DC,
    Jaw2R is R2 - DR,  Jaw2C is C2 - DC,
    is_enemy_jaw(B2, Jaw1R, Jaw1C, Enemy),
    is_enemy_jaw(B2, Jaw2R, Jaw2C, Enemy).

%%  is_enemy_jaw(+Board, +R, +C, +Enemy)

is_enemy_jaw(_, R, _, _)  :- R < 1, !.
is_enemy_jaw(_, R, _, _)  :- R > 9, !.
is_enemy_jaw(_, _, C, _)  :- C < 1, !.
is_enemy_jaw(_, _, C, _)  :- C > 9, !.
is_enemy_jaw(Board, R, C, Enemy) :-
    get_cell(Board, R, C, P),
    belongs_to(P, Enemy),
    \+ is_king(P),        
    !.
is_enemy_jaw(_, R, C, _) :-
    throne(R, C), !.
is_enemy_jaw(_, R, C, _) :-
    corner(R, C).

%%  capture_sandwiched_pieces/2
%%  Remove any non-king piece that is trapped between enemy jaws.
capture_sandwiched_pieces(Board, NewBoard) :-
    findall(R-C,
            (   between(1,9,R), between(1,9,C),
                get_cell(Board, R, C, P),
                P \= e,
                \+ is_king(P),
                belongs_to(P, PieceSide),
                other_side(PieceSide, CaptorSide),
                is_sandwiched(Board, R, C, CaptorSide)
            ),
            Sandwiched),
    remove_pieces(Board, Sandwiched, NewBoard).

is_sandwiched(Board, R, C, CaptorSide) :-
    check_capture_jaw(Board, R, C, 0, 1, CaptorSide),
    check_capture_jaw(Board, R, C, 0, -1, CaptorSide).
is_sandwiched(Board, R, C, CaptorSide) :-
    check_capture_jaw(Board, R, C, 1, 0, CaptorSide),
    check_capture_jaw(Board, R, C, -1, 0, CaptorSide).

check_capture_jaw(Board, R, C, DR, DC, CaptorSide) :-
    R1 is R + DR,
    C1 is C + DC,
    R1 >= 1, R1 =< 9,
    C1 >= 1, C1 =< 9,
    get_cell(Board, R1, C1, P),
    (
        belongs_to(P, CaptorSide)
    ;   (throne(R1, C1), get_cell(Board, R1, C1, e))
    ;   corner(R1, C1)
    ).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%   APPLY MOVE AND CAPTURES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

apply_move(Board, move(R1,C1,R2,C2), Side, NewBoard) :-
    move_piece(Board, R1, C1, R2, C2, Board1),
    perform_captures(Board1, R2, C2, Side, NewBoard).

%%  perform_captures/5
%%  Custodial capture — symmetric for both sides.
perform_captures(Board, R, C, Side, NewBoard) :-
    other_side(Side, Enemy),
    get_cell(Board, R, C, MovedPiece),
    findall(Er-Ec,
            (   member(DR-DC, [(-1)-0, 1-0, 0-(-1), 0-1]),
                Er is R + DR,
                Ec is C + DC,
                Er >= 1, Er =< 9, Ec >= 1, Ec =< 9,
                get_cell(Board, Er, Ec, EP),
                belongs_to(EP, Enemy),
                \+ is_king(EP),             %% enemy king never captured this way
                Br is Er + DR,
                Bc is Ec + DC,
                Br >= 1, Br =< 9, Bc >= 1, Bc =< 9,
                (
                    %% (a) friendly piece closes the sandwich
                    (   get_cell(Board, Br, Bc, BP),
                        belongs_to(BP, Side),
                        \+ is_king(BP)          %% king cannot assist capture
                    )
                ;
                    %% (b) vacant throne acts as jaw for either side
                    (   throne(Br, Bc),
                        get_cell(Board, Br, Bc, e)
                    )
                ;
                    %% (c) corner acts as jaw for either side
                    corner(Br, Bc)
                ),
                \+ is_king(MovedPiece)
            ),
            Captured),
    remove_pieces(Board, Captured, Board1),
    capture_sandwiched_pieces(Board1, NewBoard).

remove_pieces(Board, [], Board).
remove_pieces(Board, [R-C|Rest], NewBoard) :-
    set_cell(Board, R, C, e, Board1),
    remove_pieces(Board1, Rest, NewBoard).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  WIN / LOSS DETECTION                                             
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

king_position(Board, R, C) :-
    between(1,9,R), between(1,9,C),
    get_cell(Board, R, C, k), !.

defender_wins(Board) :-
    king_position(Board, R, C),
    corner(R, C).

attacker_wins(Board) :-
    king_position(Board, R, C),
    king_captured(Board, R, C).

king_captured(Board, R, C) :-
    findall(DR-DC, member(DR-DC, [(-1)-0, 1-0, 0-(-1), 0-1]), Dirs),
    all_sides_hostile(Board, R, C, Dirs).

all_sides_hostile(_, _, _, []).
all_sides_hostile(Board, R, C, [DR-DC|Rest]) :-
    Nr is R + DR,
    Nc is C + DC,
    (   Nr < 1 ; Nr > 9 ; Nc < 1 ; Nc > 9
    ;   hostile_to_king(Board, Nr, Nc)
    ),
    all_sides_hostile(Board, R, C, Rest).

game_over(Board, defender) :- defender_wins(Board), !.
game_over(Board, attacker) :- attacker_wins(Board), !.
game_over(Board, attacker) :- \+ king_position(Board, _, _), !.
game_over(Board, defender) :- all_moves(Board, attacker, []), !.
game_over(Board, attacker) :- all_moves(Board, defender, []), !.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%   UTILITY FUNCTION                                                  
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

evaluate(Board, Side, Score) :-
    (   defender_wins(Board)  -> RawScore = 10000
    ;   attacker_wins(Board)  -> RawScore = -10000
    ;   \+ king_position(Board,_,_) -> RawScore = -10000
    ;   compute_heuristic(Board, RawScore)
    ),
    (   Side = defender -> Score = RawScore
    ;   Score is -RawScore
    ).

compute_heuristic(Board, Score) :-
    count_pieces(Board, attacker, NumA),
    count_pieces(Board, defender, NumD),
    king_position(Board, KR, KC),
    king_corner_distance(KR, KC, CornerDist),
    king_threat_count(Board, KR, KC, Threats),
    Score is (NumD * 10)
           - (NumA * 8)
           + (CornerDist * (-4))
           - (Threats * 15).

count_pieces(Board, Side, Count) :-
    findall(1,
            (   between(1,9,R), between(1,9,C),
                get_cell(Board, R, C, P),
                belongs_to(P, Side)
            ),
            L),
    length(L, Count).

king_corner_distance(KR, KC, MinDist) :-
    findall(D,
            (   corner(CR, CC),
                D is abs(KR-CR) + abs(KC-CC)
            ),
            Dists),
    min_list(Dists, MinDist).

king_threat_count(Board, KR, KC, Count) :-
    findall(1,
            (   member(DR-DC, [(-1)-0, 1-0, 0-(-1), 0-1]),
                Nr is KR + DR,
                Nc is KC + DC,
                Nr >= 1, Nr =< 9, Nc >= 1, Nc =< 9,
                hostile_to_king(Board, Nr, Nc)
            ),
            L),
    length(L, Count).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% ALPHA-BETA PRUNING                                               
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

depth(easy,   1).
depth(medium, 2).
depth(hard,   3).

alphabeta(Board, Side, 0, _, _, null, Score) :-
    !,
    evaluate(Board, Side, Score).

alphabeta(Board, Side, _, _, _, null, Score) :-
    game_over(Board, _), !,
    evaluate(Board, Side, Score).

alphabeta(Board, Side, Depth, Alpha, Beta, BestMove, BestScore) :-
    all_moves(Board, Side, Moves),
    Moves \= [],
    other_side(Side, OpponentSide),
    D1 is Depth - 1,
    ab_loop(Moves, Board, Side, OpponentSide, D1, Alpha, Beta,
            null, -100000, BestMove, BestScore).

alphabeta(Board, Side, _, _, _, null, Score) :-
    evaluate(Board, Side, Score).

ab_loop([], _, _, _, _, _, _, BestMove, BestScore, BestMove, BestScore).

ab_loop([Move|Rest], Board, Side, OppSide, D, Alpha, Beta,
        CurBest, CurScore, BestMove, BestScore) :-
    apply_move(Board, Move, Side, NewBoard),
    (   game_over(NewBoard, _)
    ->  evaluate(NewBoard, Side, MoveScore)
    ;   NegAlpha is -Beta,
        NegBeta  is -Alpha,
        alphabeta(NewBoard, OppSide, D, NegAlpha, NegBeta, _, OppScore),
        MoveScore is -OppScore
    ),
    (   MoveScore > CurScore
    ->  NewBest  = Move,
        NewScore = MoveScore
    ;   NewBest  = CurBest,
        NewScore = CurScore
    ),
    NewAlpha is max(Alpha, NewScore),
    (   NewAlpha >= Beta
    ->  BestMove  = NewBest,
        BestScore = NewScore
    ;   ab_loop(Rest, Board, Side, OppSide, D, NewAlpha, Beta,
                NewBest, NewScore, BestMove, BestScore)
    ).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%   DISPLAY                                                           
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

print_board(Board) :-
    nl,
    write('    1   2   3   4   5   6   7   8   9'), nl,
    write('  +---+---+---+---+---+---+---+---+---+'), nl,
    print_rows(Board, 1).

print_rows([], _).
print_rows([Row|Rest], N) :-
    format('~w |', [N]),
    print_row(Row),
    nl,
    write('  +---+---+---+---+---+---+---+---+---+'), nl,
    N1 is N + 1,
    print_rows(Rest, N1).

print_row([]).
print_row([Cell|Rest]) :-
    cell_char(Cell, Ch),
    format(' ~w |', [Ch]),
    print_row(Rest).

cell_char(e, ' ').
cell_char(a, 'A').
cell_char(d, 'D').
cell_char(k, 'K').

print_status(Board) :-
    count_pieces(Board, attacker, NA),
    count_pieces(Board, defender, ND),
    format('~nAttackers remaining: ~w  |  Defenders remaining: ~w~n', [NA, ND]).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  HUMAN INPUT                                                      
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

get_human_move(Board, Side, Move) :-
    nl,
    format('Your turn (~w). Enter move as: move(Row,Col,NewRow,NewCol).~n', [Side]),
    read_term(Input, [variable_names(_)]),
    (   Input = move(R1,C1,R2,C2)
    ->  true
    ;   Input = (R1,C1,R2,C2)
    ->  true
    ;   format('Invalid format. Use: move(R1,C1,R2,C2).~n'),
        get_human_move(Board, Side, Move),
        fail
    ),
    validate_human_move(Board, Side, R1, C1, R2, C2, Move).

validate_human_move(Board, Side, R1, C1, R2, C2, Move) :-
    integer(R1), integer(C1), integer(R2), integer(C2),
    R1 >= 1, R1 =< 9, C1 >= 1, C1 =< 9,
    R2 >= 1, R2 =< 9, C2 >= 1, C2 =< 9,
    get_cell(Board, R1, C1, P),
    belongs_to(P, Side), !,
    all_moves(Board, Side, LegalMoves),
    (   member(move(R1,C1,R2,C2), LegalMoves)
    ->  Move = move(R1,C1,R2,C2)
    ;   format('Illegal move. Try again.~n'),
        get_human_move(Board, Side, Move)
    ).

validate_human_move(Board, Side, _, _, _, _, Move) :-
    format('That piece does not belong to you or coordinates are wrong. Try again.~n'),
    get_human_move(Board, Side, Move).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%   COMPUTER MOVE                                                    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

get_computer_move(Board, Side, Difficulty, Move) :-
    depth(Difficulty, D),
    format('~nComputer (~w) is thinking...~n', [Side]),
    alphabeta(Board, Side, D, -100000, 100000, Move, _),
    (   Move = null
    ->  format('Computer has no valid move!~n'), fail
    ;   Move = move(R1,C1,R2,C2),
        format('Computer moves: (~w,~w) -> (~w,~w)~n', [R1,C1,R2,C2])
    ).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%   GAME LOOP                                                        
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

game_loop(Board, CurrentSide, HumanSide, Difficulty) :-
    print_board(Board),
    print_status(Board),
    (   game_over(Board, Winner)
    ->  nl,
        format('*** GAME OVER! Winner: ~w ***~n', [Winner])
    ;   make_move(Board, CurrentSide, HumanSide, Difficulty, NewBoard),
        other_side(CurrentSide, NextSide),
        game_loop(NewBoard, NextSide, HumanSide, Difficulty)
    ).

make_move(Board, CurrentSide, HumanSide, _, NewBoard) :-
    CurrentSide = HumanSide, !,
    get_human_move(Board, CurrentSide, Move),
    apply_move(Board, Move, CurrentSide, NewBoard).

make_move(Board, CurrentSide, _, Difficulty, NewBoard) :-
    get_computer_move(Board, CurrentSide, Difficulty, Move),
    apply_move(Board, Move, CurrentSide, NewBoard).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  SETUP AND ENTRY POINT                                           
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

play :-
    nl,
    write('========================================='), nl,
    write('   HNEFATAFL - Viking Chess (9x9)        '), nl,
    write('========================================='), nl,
    choose_human_side(HumanSide),
    choose_difficulty(Difficulty),
    format('~nYou play as: ~w~n', [HumanSide]),
    format('Difficulty : ~w~n', [Difficulty]),
    nl,
    write('HOW TO ENTER A MOVE:'), nl,
    write('  Type: move(Row,Col,NewRow,NewCol).'), nl,
    write('  Example: move(5,3,5,1).'), nl,
    write('  Pieces: A=Attacker, D=Defender, K=King'), nl,
    nl,
    write('Attackers always go first.'), nl,
    initial_board(Board),
    game_loop(Board, attacker, HumanSide, Difficulty).

choose_human_side(Side) :-
    nl,
    write('Choose your side:'), nl,
    write('  1. Attacker (Black - moves first)'), nl,
    write('  2. Defender (White)'), nl,
    write('Enter 1 or 2: '),
    read(Choice),
    (   Choice =:= 1 -> Side = attacker
    ;   Choice =:= 2 -> Side = defender
    ;   write('Invalid choice, defaulting to attacker.'), nl, Side = attacker
    ).

choose_difficulty(Difficulty) :-
    nl,
    write('Choose difficulty:'), nl,
    write('  1. Easy   (depth 1)'), nl,
    write('  2. Medium (depth 2)'), nl,
    write('  3. Hard   (depth 3)'), nl,
    write('Enter 1, 2 or 3: '),
    read(DChoice),
    (   DChoice =:= 1 -> Difficulty = easy
    ;   DChoice =:= 2 -> Difficulty = medium
    ;   DChoice =:= 3 -> Difficulty = hard
    ;   write('Invalid choice, defaulting to easy.'), nl, Difficulty = easy
    ).
