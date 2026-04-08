from move import Move
from collections import deque

DELTAS = {
    Move.UP:    (-1,  0),
    Move.DOWN:  ( 1,  0),
    Move.RIGHT: ( 0,  1),
    Move.LEFT:  ( 0, -1),
}


class Group19:

    def __init__(self, maze, prize_positions, agent_position, opponent_position, max_turns):
        self.path = deque()
        self.target = None
        self.rows = len(maze)
        self.cols = len(maze[0])

    # ------------------------------------------------------------
    # Manhattan distance
    # ------------------------------------------------------------
    def _manhattan(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # ------------------------------------------------------------
    # Greedy step (rápido tipo SimpleHC)
    # ------------------------------------------------------------
    def _greedy_step(self, maze, agent_pos, prize_positions):
        row, col = agent_pos

        def best_dist(r, c):
            return min(self._manhattan((r, c), p) for p in prize_positions)

        best_move = Move.STAY
        best_val = float('inf')

        for move, (dr, dc) in DELTAS.items():
            nr, nc = row + dr, col + dc

            if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                continue
            if maze[nr][nc] == '#':
                continue

            dist = best_dist(nr, nc)

            if dist < best_val:
                best_val = dist
                best_move = move

        return best_move

    # ------------------------------------------------------------
    # BFS path (usado raramente)
    # ------------------------------------------------------------
    def _bfs_path(self, maze, start, goal):
        if start == goal:
            return deque()

        visited = {start: None}
        queue = deque([start])

        while queue:
            r, c = queue.popleft()

            for move, (dr, dc) in DELTAS.items():
                nr, nc = r + dr, c + dc
                pos = (nr, nc)

                if pos in visited:
                    continue
                if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                    continue
                if maze[nr][nc] == '#':
                    continue

                visited[pos] = ((r, c), move)

                if pos == goal:
                    path = deque()
                    cur = pos
                    while visited[cur] is not None:
                        parent, mv = visited[cur]
                        path.appendleft(mv)
                        cur = parent
                    return path

                queue.append(pos)

        return deque()

    # ------------------------------------------------------------
    # Escolha de target (leve e rápida)
    # ------------------------------------------------------------
    def _choose_target(self, agent_pos, opponent_pos, prize_positions):
        best_target = None
        best_score = -float('inf')

        for p, val in prize_positions.items():
            d_me = self._manhattan(agent_pos, p)
            d_opp = self._manhattan(opponent_pos, p)

            if d_me == 0:
                return p

            score = val / d_me

            # Penalizar se adversário estiver mais perto
            if d_opp < d_me:
                score *= 0.3

            # Incentivar disputa direta
            elif d_opp == d_me:
                score *= 1.2

            if score > best_score:
                best_score = score
                best_target = p

        return best_target

    # ------------------------------------------------------------
    # Replaneamento leve
    # ------------------------------------------------------------
    def _should_replan(self, prize_positions):
        if self.target not in prize_positions:
            return True
        if not self.path:
            return True
        return False

    # ------------------------------------------------------------
    # MAIN
    # ------------------------------------------------------------
    def next_move(self, maze, prize_positions, agent_position, opponent_position):

        if not prize_positions:
            return Move.STAY

        # Replanear apenas quando necessário
        if self._should_replan(prize_positions):
            self.target = self._choose_target(agent_position, opponent_position, prize_positions)

            # Só usa BFS se estiver longe (evita custo desnecessário)
            if self._manhattan(agent_position, self.target) > 4:
                self.path = self._bfs_path(maze, agent_position, self.target)
            else:
                self.path = deque()

        # Se temos caminho → seguir
        if self.path:
            move = self.path.popleft()
        else:
            move = self._greedy_step(maze, agent_position, prize_positions)

        # Segurança
        dr, dc = DELTAS[move]
        nr, nc = agent_position[0] + dr, agent_position[1] + dc

        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            return Move.STAY
        if maze[nr][nc] == '#':
            return Move.STAY

        return move