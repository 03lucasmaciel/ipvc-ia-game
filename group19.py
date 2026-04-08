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
        self.rows = len(maze)
        self.cols = len(maze[0])

    # ------------------------------------------------------------
    # BFS completo (UMA VEZ POR TURNO)
    # ------------------------------------------------------------
    def _bfs(self, maze, start):
        dist = {start: 0}
        parent = {start: None}
        move_map = {}

        queue = deque([start])

        while queue:
            r, c = queue.popleft()

            for move, (dr, dc) in DELTAS.items():
                nr, nc = r + dr, c + dc
                pos = (nr, nc)

                if pos in dist:
                    continue
                if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                    continue
                if maze[nr][nc] == '#':
                    continue

                dist[pos] = dist[(r, c)] + 1
                parent[pos] = (r, c)
                move_map[pos] = move
                queue.append(pos)

        return dist, parent, move_map

    # ------------------------------------------------------------
    # reconstruir caminho
    # ------------------------------------------------------------
    def _get_first_move(self, parent, move_map, start, goal):
        cur = goal
        while parent[cur] != start:
            cur = parent[cur]
        return move_map[cur]

    # ------------------------------------------------------------
    # MAIN
    # ------------------------------------------------------------
    def next_move(self, maze, prize_positions, agent_position, opponent_position):

        if not prize_positions:
            return Move.STAY

        # BFS global
        dist, parent, move_map = self._bfs(maze, agent_position)

        best_target = None
        best_score = -1

        for p, val in prize_positions.items():
            if p not in dist:
                continue

            d = dist[p]
            if d == 0:
                return Move.STAY

            score = val / d

            # leve consideração do adversário
            opp_dist = abs(opponent_position[0] - p[0]) + abs(opponent_position[1] - p[1])
            if opp_dist < d:
                score *= 0.7

            if score > best_score:
                best_score = score
                best_target = p

        if best_target is None:
            return Move.STAY

        return self._get_first_move(parent, move_map, agent_position, best_target)