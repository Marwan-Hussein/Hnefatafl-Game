# ai/evaluation.py
#utility function here
# You implement:
# - board scoring function
# - evaluates a game state from a given player's perspective
# - heuristics:
#     * material advantage (attackers vs defenders)
#     * king safety (distance to escape corners)
#     * positional advantage
#
# Goal:
# - assign a numeric score to any board state
# - used by alpha-beta pruning to choose best move