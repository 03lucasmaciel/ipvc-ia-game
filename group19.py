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

    def _can_move_to(self, maze, pos):
        """Verifica se pode mover para uma posição."""
        r, c = pos
        return (0 <= r < self.rows and 0 <= c < self.cols and maze[r][c] != '#')

    def _manhattan_dist(self, p1, p2):
        """Distância de Manhattan."""
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def next_move(self, maze, prize_positions, agent_position, opponent_position):
        """
        Estratégia: Seleciona o melhor prémio reachable (por BFS distance),
        depois segue o caminho BFS para ele.
        OTIMIZADO: Calcula BFS UMA VEZ desde agent_position para todos os prémios.
        MELHORADO: Tie-breaking por distância quando scores são iguais (dentro de 1%)
        """
        if not prize_positions:
            return Move.STAY

        agent_row, agent_col = agent_position
        
        # OTIMIZAÇÃO: Calcular BFS uma única vez desde a posição do agente
        bfs_dist_map = self._bfs_distances_all(maze, agent_position)
        
        # Encontrar o melhor prémio reachable
        best_prize = None
        best_score = -1
        best_distance = float('inf')
        
        for prize_pos, prize_value in prize_positions.items():
            bfs_dist = bfs_dist_map.get(prize_pos, -1)
            
            if bfs_dist == -1:  # Não reachable
                continue
            
            if bfs_dist == 0:  # Está ON TOP
                return Move.STAY
            
            # Score: value / (distance ^ 1.2)
            # Aumento significativo do peso da distância para favorecer prémios próximos
            # Isto ajuda contra simpleHC em mazes pequenos
            score = prize_value / (bfs_dist ** 1.2)
            
            # Tie-breaking: se scores são muito próximos (dif < 1%), preferir mais próximo
            if best_prize is not None:
                score_diff_percent = abs(score - best_score) / best_score * 100
                if score_diff_percent < 1:  # Scores praticamente iguais
                    # Preferir o mais próximo
                    if bfs_dist < best_distance:
                        best_score = score
                        best_prize = prize_pos
                        best_distance = bfs_dist
                elif score > best_score:
                    best_score = score
                    best_prize = prize_pos
                    best_distance = bfs_dist
            else:
                best_score = score
                best_prize = prize_pos
                best_distance = bfs_dist

        if best_prize is None:
            # Nenhum prémio reachable, explorar
            for move in [Move.DOWN, Move.RIGHT, Move.UP, Move.LEFT]:
                dr, dc = DELTAS[move]
                new_pos = (agent_row + dr, agent_col + dc)
                if self._can_move_to(maze, new_pos):
                    return move
            return Move.STAY

        # Move um passo em direção ao melhor prémio usando BFS path
        path = self._bfs_path(maze, agent_position, best_prize)
        if path and len(path) > 1:
            next_pos = path[1]
            dr = next_pos[0] - agent_row
            dc = next_pos[1] - agent_col
            
            for move_enum, (delta_r, delta_c) in DELTAS.items():
                if delta_r == dr and delta_c == dc:
                    return move_enum
        
        return Move.STAY

    def _bfs_distances_all(self, maze, start):
        """Retorna um dicionário de todas as distâncias BFS desde start."""
        distances = {start: 0}
        queue = deque([start])
        
        while queue:
            pos = queue.popleft()
            r, c = pos
            current_dist = distances[pos]
            
            for move, (dr, dc) in DELTAS.items():
                nr, nc = r + dr, c + dc
                new_pos = (nr, nc)
                
                if new_pos not in distances and self._can_move_to(maze, new_pos):
                    distances[new_pos] = current_dist + 1
                    queue.append(new_pos)
        
        return distances

    def _bfs_path(self, maze, start, end):
        """Retorna o caminho BFS mais curto entre start e end."""
        if start == end:
            return [start]
        
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            pos, path = queue.popleft()
            r, c = pos
            
            for move, (dr, dc) in DELTAS.items():
                nr, nc = r + dr, c + dc
                new_pos = (nr, nc)
                
                if new_pos == end:
                    return path + [new_pos]
                
                if new_pos not in visited and self._can_move_to(maze, new_pos):
                    visited.add(new_pos)
                    queue.append((new_pos, path + [new_pos]))
        
        return []  # Não reachable                                          