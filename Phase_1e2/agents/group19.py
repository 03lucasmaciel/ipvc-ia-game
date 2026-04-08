from move import Move
from collections import deque

DELTAS = {
    Move.UP: (-1, 0),
    Move.DOWN: (1, 0),
    Move.RIGHT: (0, 1),
    Move.LEFT: (0, -1)
}


class Group19:

    def __init__(self, maze, prize_positions, agent_position, opponent_position, max_turns):
        self.path = []
        self.target = None

    def next_move(self, maze, prize_positions, agent_position, opponent_position):

        if not prize_positions:
            return Move.STAY
        
        if not self.path or self.target not in prize_positions:
            self.target, self.path = self._pick_best_target(
                maze, prize_positions, agent_position
            )
        
        if not self.path:
            return Move.STAY
        
        return self.path.pop(0)
    
    def _pick_best_target(self, maze, prize_positions, agent_position):
        
        best_target = None
        best_path = None
        best_ratio = -1

        for prize_pos, prize_val in prize_positions.items():
            path = self._bfs(maze, agent_position, prize_pos)
            if path is None:
                continue
            dist = len(path)
            if dist == 0:
                continue
            ratio = prize_val / dist
            if ratio > best_ratio: 
                best_ratio = ratio
                best_target = prize_pos
                best_path = path
        
        return best_target, (best_path if best_path else [])
    
    def _bfs(self, maze, start, goal):
        if start == goal:
            return []
        
        num_rows = len(maze)
        num_cols = len(maze[0])

        visited = {start: None}
        queue = deque([start])

        while queue:
            pos = queue.popleft()
            row, col = pos

            for move, (dr, dc) in DELTAS.items():
                new_row, new_col = row + dr, col + dc
                new_pos = (new_row, new_col)

                if new_pos in visited:
                    continue
                if not (0 <= new_row < num_rows and 0 <= new_col < num_cols):
                    continue
                if maze[new_row][new_col] == '#':
                    continue

                visited[new_pos] = (pos, move)

                if new_pos == goal:
                    path = []
                    cur = new_pos
                    while visited[cur] is not None:
                        parent, mv = visited[cur]
                        path.append(mv)
                        cur = parent
                    path.reverse()
                    return path
                
                queue.append(new_pos)

        return None