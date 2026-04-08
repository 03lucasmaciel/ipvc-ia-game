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
        self.max_turns = max_turns
        self.path = []
        self.target = None

        self._num_rows = len(maze)
        self._num_cols = len(maze[0])

        # Cache de distâncias BFS: start -> {pos: dist}
        self._dist_cache = {}

        # Pré-computar distâncias a partir da posição do agente, do adversário
        # e de todos os prémios — next_move nunca precisa de correr BFS de raiz
        all_starts = (
            [agent_position, opponent_position]
            + list(prize_positions.keys())
        )
        for pos in all_starts:
            if pos not in self._dist_cache:
                self._dist_cache[pos] = self._bfs_distances(maze, pos)

    # ------------------------------------------------------------------
    # BFS completo: devolve {pos: distância} a partir de start
    # ------------------------------------------------------------------
    def _bfs_distances(self, maze, start):
        dist = {start: 0}
        queue = deque([start])
        num_rows = len(maze)
        num_cols = len(maze[0])
        while queue:
            pos = queue.popleft()
            r, c = pos
            for dr, dc in DELTAS.values():
                nr, nc = r + dr, c + dc
                npos = (nr, nc)
                if npos in dist:
                    continue
                if not (0 <= nr < num_rows and 0 <= nc < num_cols):
                    continue
                if maze[nr][nc] == '#':
                    continue
                dist[npos] = dist[pos] + 1
                queue.append(npos)
        return dist

    # ------------------------------------------------------------------
    # BFS que devolve o caminho (lista de Move) de start até goal
    # ------------------------------------------------------------------
    def _bfs_path(self, maze, start, goal):
        if start == goal:
            return []
        num_rows = len(maze)
        num_cols = len(maze[0])
        visited = {start: None}
        queue = deque([start])
        while queue:
            pos = queue.popleft()
            r, c = pos
            for move, (dr, dc) in DELTAS.items():
                nr, nc = r + dr, c + dc
                npos = (nr, nc)
                if npos in visited:
                    continue
                if not (0 <= nr < num_rows and 0 <= nc < num_cols):
                    continue
                if maze[nr][nc] == '#':
                    continue
                visited[npos] = (pos, move)
                if npos == goal:
                    path = []
                    cur = npos
                    while visited[cur] is not None:
                        parent, mv = visited[cur]
                        path.append(mv)
                        cur = parent
                    path.reverse()
                    return path
                queue.append(npos)
        return None

    # ------------------------------------------------------------------
    # Distância BFS com cache (lazy para posições mid-game)
    # ------------------------------------------------------------------
    def _get_dist(self, maze, frm, to):
        if frm not in self._dist_cache:
            self._dist_cache[frm] = self._bfs_distances(maze, frm)
        return self._dist_cache[frm].get(to, float('inf'))

    # ------------------------------------------------------------------
    # Scoring de um prémio face ao estado atual
    #
    # Lógica:
    #   advantage > 1  → prémio "nosso"   → score = val/dist + bónus territorial
    #   advantage >= -1 → corrida apertada → score moderado
    #   advantage < -1  → prémio "dele"   → score muito penalizado
    # ------------------------------------------------------------------
    def _score_prize(self, dist_me, dist_opp, prize_val):
        if dist_me == float('inf'):
            return -float('inf')

        advantage = dist_opp - dist_me  # positivo = chegamos antes

        if advantage > 1:
            # Prémio garantido — maximizar ratio e recompensar vantagem territorial
            base = prize_val / dist_me
            territorial_bonus = min(advantage * 0.3, 2.0)
            return base + territorial_bonus

        elif advantage >= -1:
            # Corrida apertada — ainda pode compensar para valores altos
            base = prize_val / dist_me
            return base * 0.6

        else:
            # Adversário chega bem antes — só ir se não há nada melhor
            base = prize_val / dist_me
            return base * 0.05

    # ------------------------------------------------------------------
    # Escolhe o melhor target com base no scoring
    # ------------------------------------------------------------------
    def _pick_best_target(self, maze, prize_positions, agent_pos, opponent_pos):
        best_target = None
        best_score = -float('inf')

        for prize_pos, prize_val in prize_positions.items():
            dist_me = self._get_dist(maze, agent_pos, prize_pos)
            dist_opp = self._get_dist(maze, opponent_pos, prize_pos)
            score = self._score_prize(dist_me, dist_opp, prize_val)

            if score > best_score:
                best_score = score
                best_target = prize_pos

        if best_target is None:
            return None, []

        path = self._bfs_path(maze, agent_pos, best_target)
        return best_target, (path if path else [])

    # ------------------------------------------------------------------
    # Decide se deve replanear
    # ------------------------------------------------------------------
    def _should_replan(self, maze, prize_positions, agent_pos, opponent_pos):
        if self.target not in prize_positions:
            return True
        if not self.path:
            return True
        # Adversário interceptou — vai chegar antes
        dist_opp = self._get_dist(maze, opponent_pos, self.target)
        if dist_opp < len(self.path) - 1:
            return True
        return False

    # ------------------------------------------------------------------
    # next_move principal
    # ------------------------------------------------------------------
    def next_move(self, maze, prize_positions, agent_position, opponent_position):
        if not prize_positions:
            return Move.STAY

        if self._should_replan(maze, prize_positions, agent_position, opponent_position):
            self.target, self.path = self._pick_best_target(
                maze, prize_positions, agent_position, opponent_position
            )

        if not self.path:
            return Move.STAY

        # Verificação de segurança: próximo passo não é parede
        next_action = self.path[0]
        dr, dc = DELTAS[next_action]
        r, c = agent_position
        nr, nc = r + dr, c + dc
        if not (0 <= nr < self._num_rows and 0 <= nc < self._num_cols):
            self.path = []
            self.target = None
            return Move.STAY
        if maze[nr][nc] == '#':
            self.path = []
            self.target = None
            return Move.STAY

        return self.path.pop(0)
