from move import Move

DELTAS = {
    Move.UP:    (-1,  0),
    Move.DOWN:  ( 1,  0),
    Move.RIGHT: ( 0,  1),
    Move.LEFT:  ( 0, -1),
}


class Group19:

    def __init__(self, maze, prize_positions, agent_position, opponent_position, max_turns):
        self.rows = len(maze)
        self.cols = len(maze[0])

    # Manhattan
    def _manhattan(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Escolher melhor prémio (ULTRA RÁPIDO)
    def _best_target(self, agent_pos, opponent_pos, prize_positions):
        best = None
        best_score = -1

        for p, val in prize_positions.items():
            d_me = self._manhattan(agent_pos, p)
            d_opp = self._manhattan(opponent_pos, p)

            if d_me == 0:
                return p

            score = val / d_me

            # pequena inteligência contra adversário (leve!)
            if d_opp < d_me:
                score *= 0.5

            if score > best_score:
                best_score = score
                best = p

        return best

    # Movimento greedy (tipo SimpleHC mas melhor)
    def _move_towards(self, maze, agent_pos, target):
        r, c = agent_pos

        best_move = Move.STAY
        best_dist = float('inf')

        for move, (dr, dc) in DELTAS.items():
            nr, nc = r + dr, c + dc

            if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                continue
            if maze[nr][nc] == '#':
                continue

            d = self._manhattan((nr, nc), target)

            if d < best_dist:
                best_dist = d
                best_move = move

        return best_move

    # MAIN
    def next_move(self, maze, prize_positions, agent_position, opponent_position):

        if not prize_positions:
            return Move.STAY

        target = self._best_target(agent_position, opponent_position, prize_positions)

        if not target:
            return Move.STAY

        return self._move_towards(maze, agent_position, target)