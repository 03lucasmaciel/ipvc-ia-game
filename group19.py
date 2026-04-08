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
        self.turn = 0

        # Divisão do mapa (território)
        self.mid_col = self.cols // 2

    # ------------------------------------------------------------
    # Manhattan
    # ------------------------------------------------------------
    def _manhattan(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # ------------------------------------------------------------
    # Território (evita cruzar mapa sem necessidade)
    # ------------------------------------------------------------
    def _territory_weight(self, agent_pos, prize_pos):
        if agent_pos[1] < self.mid_col:
            return 0.5 if prize_pos[1] > self.mid_col else 1.0
        else:
            return 0.5 if prize_pos[1] < self.mid_col else 1.0

    # ------------------------------------------------------------
    # Greedy rápido (tipo SimpleHC mas melhor)
    # ------------------------------------------------------------
    def _greedy_step(self, maze, agent_pos, prize_positions):
        r, c = agent_pos

        def best_dist(nr, nc):
            return min(self._manhattan((nr, nc), p) for p in prize_positions)

        best_move = Move.STAY
        best_val = float('inf')

        for move, (dr, dc) in DELTAS.items():
            nr, nc = r + dr, c + dc

            if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                continue
            if maze[nr][nc] == '#':
                continue

            d = best_dist(nr, nc)

            if d < best_val:
                best_val = d
                best_move = move

        return best_move

    # ------------------------------------------------------------
    # BFS path (só quando necessário)
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
    # Escolha de target (core da inteligência)
    # ------------------------------------------------------------
    def _choose_target(self, agent_pos, opponent_pos, prize_positions):
        best_target = None
        best_score = -float('inf')

        for p, val in prize_positions.items():
            d_me = self._manhattan(agent_pos, p)
            d_opp = self._manhattan(opponent_pos, p)

            if d_me == 0:
                return p

            # Base
            score = val / d_me

            # Early game: agressivo
            if self.turn < 10:
                score *= 1.5

            # Território
            score *= self._territory_weight(agent_pos, p)

            # Adversário
            if d_opp < d_me:
                score *= 0.3
            elif d_opp == d_me:
                score *= 1.2

            # Prioridade a prémios próximos
            if d_me <= 2:
                score += 5

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

        self.turn += 1

        if not prize_positions:
            return Move.STAY

        # Escolher novo alvo se necessário
        if self._should_replan(prize_positions):
            self.target = self._choose_target(agent_position, opponent_position, prize_positions)

            if self.target:
                # Só usar BFS se estiver longe
                if self._manhattan(agent_position, self.target) > 4:
                    self.path = self._bfs_path(maze, agent_position, self.target)
                else:
                    self.path = deque()

        # Seguir caminho se existir
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