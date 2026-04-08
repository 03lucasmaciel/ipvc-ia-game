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

    def _bfs_limited(self, maze, start, max_depth=6):
        """
        BFS limitado até profundidade max_depth.
        Retorna distância real (através de caminhos).
        Profundidade reduzida para 6 por performance.
        """
        dist = {start: 0}
        queue = deque([start])
        depth_count = {start: 0}

        while queue:
            pos = queue.popleft()
            current_depth = depth_count[pos]
            
            if current_depth >= max_depth:
                continue

            r, c = pos
            for move, (dr, dc) in DELTAS.items():
                nr, nc = r + dr, c + dc
                new_pos = (nr, nc)

                if new_pos in dist:
                    continue
                if not self._can_move_to(maze, new_pos):
                    continue

                dist[new_pos] = dist[pos] + 1
                depth_count[new_pos] = current_depth + 1
                queue.append(new_pos)

        return dist

    def next_move(self, maze, prize_positions, agent_position, opponent_position):
        """
        Estratégia: Greedy com BFS limitado (profundidade 6).
        Para cada movimento possível, calcula score baseado:
        1. Distância real ao melhor prémio (BFS)
        2. Valor do prémio (pesa mais se >= 7)
        3. Competição com adversário
        """
        if not prize_positions:
            return Move.STAY

        best_move = Move.STAY
        best_score = float('-inf')

        for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            dr, dc = DELTAS[move]
            new_pos = (agent_position[0] + dr, agent_position[1] + dc)
            
            if not self._can_move_to(maze, new_pos):
                continue

            # BFS limitado a partir da nova posição
            dist_map = self._bfs_limited(maze, new_pos, max_depth=6)

            # Encontra o melhor prémio acessível
            best_score_move = float('-inf')
            
            for prize_pos, prize_value in prize_positions.items():
                # Usa distância real se BFS chegou
                if prize_pos in dist_map:
                    dist = dist_map[prize_pos]
                else:
                    # Fallback: Manhattan + penalidade por estar longe/inacessível
                    dist = self._manhattan_dist(new_pos, prize_pos) + 3
                
                if dist == 0:
                    # Prémio na posição! Retornar imediatamente
                    return move
                
                # Premia prémios de alto valor AGRESSIVAMENTE (A=10 até F=15)
                # Aumenta multiplicador para priorizar prémios valiosos
                if prize_value >= 10:
                    score = (prize_value * 3.0) / dist  # Aumentado de 1.5 para 3.0
                elif prize_value >= 7:
                    score = (prize_value * 2.0) / dist  # Aumentado de 1.5 para 2.0
                else:
                    score = (prize_value * 1.2) / dist  # Pequeno multiplicador para baixos
                
                # Penalidade apenas se adversário está MUITO perto (dist <= 2)
                opp_dist = self._manhattan_dist(opponent_position, prize_pos)
                if opp_dist <= 2 and opp_dist < dist:
                    score *= 0.75  # Penalidade mais severa se adversário está muito perto
                elif opp_dist < dist and opp_dist <= 5:
                    score *= 0.9   # Penalidade leve se adversário está moderadamente perto
                
                if score > best_score_move:
                    best_score_move = score
            
            if best_score_move > best_score:
                best_score = best_score_move
                best_move = move

        return best_move