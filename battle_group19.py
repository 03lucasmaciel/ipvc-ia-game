#!/usr/bin/env python3
"""
Script para testar Group19 contra todos os outros agentes em todos os mazes.
Executa batalhas apenas com Group19 em ambas as posições (player1 e player2).

Estrutura:
- Procura mazes em cada versão/subfolder
- Identifica agentes disponíveis nessa pasta
- Executa: group19 vs agente1, agente1 vs group19, etc.
- Guarda resultados com análise detalhada
"""

import subprocess
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class Group19Tournament:
    def __init__(self):
        self.workspace_root = Path(__file__).parent
        self.results = []
        self.summary = {}
        
    def find_all_mazes(self):
        """Encontra todos os mazes em todas as pastas."""
        mazes_by_folder = {}
        
        for version_dir in self.workspace_root.iterdir():
            if not version_dir.is_dir() or version_dir.name.startswith("_"):
                continue
            
            mazes_dir = version_dir / "mazes"
            if not mazes_dir.exists():
                continue
            
            # Procurar todos os .txt em mazes
            mazes = sorted([f.name for f in mazes_dir.glob("*.txt")])
            
            if mazes:
                mazes_by_folder[str(version_dir)] = {
                    "folder_name": version_dir.name,
                    "mazes": mazes,
                    "mazes_path": str(mazes_dir)
                }
        
        return mazes_by_folder
    
    def get_agents(self, version_dir):
        """Extrai nomes dos agentes disponíveis numa versão."""
        agents_dir = version_dir / "agents"
        agents = []
        
        for file in agents_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            agent_name = file.stem
            
            # Remover sufixo "_agent" se existir
            if agent_name.endswith("_agent"):
                agent_name = agent_name[:-6]
            
            # Remover "group" agents (vamos testar apenas group19)
            if agent_name.startswith("group"):
                continue
            
            agents.append(agent_name)
        
        return sorted(agents)
    
    def run_battle(self, version_dir, maze_path, agent1, agent2):
        """Executa uma batalha entre dois agentes."""
        run_script = version_dir / "run.py"
        
        cmd = [
            "python3",
            str(run_script),
            str(maze_path),
            "200",  # max_turns
            agent1,
            agent2
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(version_dir)
            )
            
            output = result.stdout + result.stderr
            return {
                "status": "success",
                "returncode": result.returncode,
                "output": output
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "returncode": -1,
                "output": "Timeout after 30 seconds"
            }
        except Exception as e:
            return {
                "status": "error",
                "returncode": -1,
                "output": str(e)
            }
    
    def extract_scores(self, output):
        """Extrai scores do output de uma batalha."""
        try:
            # Procurar por padrão "Agent 1 (...): X pts" e "Agent 2 (...): Y pts"
            agent1_match = re.search(r'Agent 1[^:]*:\s+(\d+)\s+pts', output)
            agent2_match = re.search(r'Agent 2[^:]*:\s+(\d+)\s+pts', output)
            
            if agent1_match and agent2_match:
                s1 = int(agent1_match.group(1))
                s2 = int(agent2_match.group(1))
                return s1, s2
        except:
            pass
        
        return None, None
    
    def determine_winner(self, score1, score2, player1, player2):
        """Determina o vencedor."""
        if score1 is None or score2 is None:
            return None, None, False
        
        if score1 > score2:
            return player1, score1, False
        elif score2 > score1:
            return player2, score2, False
        else:
            return None, score1, True
    
    def run_tournament(self):
        """Executa o torneio com apenas Group19."""
        print("=" * 90)
        print("TORNEIO GROUP19 vs AGENTES")
        print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 90)
        
        all_mazes = self.find_all_mazes()
        battle_num = 0
        
        if not all_mazes:
            print("❌ Nenhum maze encontrado!")
            return
        
        for version_path, maze_info in sorted(all_mazes.items()):
            version_dir = Path(version_path)
            version_name = maze_info['folder_name']
            
            print(f"\n📂 {version_name}")
            print("-" * 90)
            
            # Obter agentes disponíveis
            agents = self.get_agents(version_dir)
            
            if not agents:
                print(f"   ⚠️  Nenhum agente encontrado em {version_name}")
                continue
            
            print(f"   Agentes: {', '.join(agents)}")
            
            # Testar cada maze
            for maze_name in maze_info['mazes']:
                maze_path = Path(maze_info['mazes_path']) / maze_name
                
                # Testar group19 vs cada agente
                for opponent in agents:
                    # Battle 1: group19 vs opponent
                    battle_num += 1
                    key = f"{version_name}_{maze_name}_group19_vs_{opponent}"
                    
                    print(f"   [{battle_num}] {maze_name:20} | group19 vs {opponent:15} ", end="", flush=True)
                    
                    result = self.run_battle(version_dir, maze_path, "group19", opponent)
                    
                    battle_data = {
                        "battle_id": battle_num,
                        "version": version_name,
                        "maze": maze_name,
                        "player1": "group19",
                        "player2": opponent,
                        "result": result
                    }
                    
                    score1, score2 = self.extract_scores(result['output'])
                    battle_data['score1'] = score1
                    battle_data['score2'] = score2
                    winner, points, is_draw = self.determine_winner(score1, score2, "group19", opponent)
                    battle_data['winner'] = winner
                    
                    self.results.append(battle_data)
                    
                    status_emoji = "✓" if result["status"] == "success" else "✗"
                    result_str = f"({score1}-{score2})" if score1 is not None else "(N/A)"
                    print(f"{status_emoji} {result_str}")
                    
                    # Battle 2: opponent vs group19 (posição Y)
                    battle_num += 1
                    print(f"   [{battle_num}] {maze_name:20} | {opponent:15} vs group19 ", end="", flush=True)
                    
                    result = self.run_battle(version_dir, maze_path, opponent, "group19")
                    
                    battle_data = {
                        "battle_id": battle_num,
                        "version": version_name,
                        "maze": maze_name,
                        "player1": opponent,
                        "player2": "group19",
                        "result": result
                    }
                    
                    score1, score2 = self.extract_scores(result['output'])
                    battle_data['score1'] = score1
                    battle_data['score2'] = score2
                    winner, points, is_draw = self.determine_winner(score1, score2, opponent, "group19")
                    battle_data['winner'] = winner
                    
                    self.results.append(battle_data)
                    
                    status_emoji = "✓" if result["status"] == "success" else "✗"
                    result_str = f"({score1}-{score2})" if score1 is not None else "(N/A)"
                    print(f"{status_emoji} {result_str}")
        
        print("\n" + "=" * 90)
        print(f"TORNEIO COMPLETO: {battle_num} batalhas executadas")
        print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 90)
        
        self.save_results()
        self.print_summary()
    
    def save_results(self):
        """Guarda resultados em JSON."""
        filename = f"group19_tournament_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.workspace_root / filename
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_battles": len(self.results),
            "battles": self.results
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Resultados guardados em: {filename}")
    
    def print_summary(self):
        """Imprime um resumo do torneio."""
        successful = sum(1 for r in self.results if r['result']['status'] == 'success')
        
        # Contar vitórias/derrotas do group19
        group19_wins = sum(1 for r in self.results if r['winner'] == 'group19')
        group19_losses = sum(1 for r in self.results if r['winner'] is not None and r['winner'] != 'group19')
        group19_draws = sum(1 for r in self.results if r['winner'] is None and r['score1'] is not None)
        group19_games = sum(1 for r in self.results if r['score1'] is not None)
        
        print("\n📊 RESUMO DO TORNEIO GROUP19:")
        print("-" * 90)
        print(f"Total de batalhas: {len(self.results)}")
        print(f"Batalhas bem-sucedidas: {successful}/{len(self.results)}")
        print(f"Taxa de sucesso: {(successful/len(self.results)*100):.1f}%\n")
        
        print(f"GROUP19 STATS:")
        print(f"  Vitórias: {group19_wins}")
        print(f"  Derrotas: {group19_losses}")
        print(f"  Empates: {group19_draws}")
        print(f"  Total de matches: {group19_games}")
        if group19_games > 0:
            print(f"  Taxa de vitória: {(group19_wins/group19_games*100):.1f}%")
        
        # Estatísticas por agente
        print(f"\nRESULTADOS CONTRA AGENTES:")
        print(f"{'Agente':<15} {'Vitórias':<12} {'Derrotas':<12} {'Empates':<10} {'Taxa Vitória':<15}")
        print("-" * 90)
        
        opponent_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0})
        
        for result in self.results:
            if result['score1'] is None:
                continue
            
            if result['player1'] == 'group19':
                opponent = result['player2']
                if result['winner'] == 'group19':
                    opponent_stats[opponent]['losses'] += 1
                elif result['winner'] == opponent:
                    opponent_stats[opponent]['wins'] += 1
                else:
                    opponent_stats[opponent]['draws'] += 1
            else:
                opponent = result['player1']
                if result['winner'] == opponent:
                    opponent_stats[opponent]['losses'] += 1
                elif result['winner'] == 'group19':
                    opponent_stats[opponent]['wins'] += 1
                else:
                    opponent_stats[opponent]['draws'] += 1
        
        for opponent in sorted(opponent_stats.keys()):
            stats = opponent_stats[opponent]
            total = stats['wins'] + stats['losses'] + stats['draws']
            win_rate = (stats['wins'] / total * 100) if total > 0 else 0
            print(f"{opponent:<15} {stats['losses']:<12} {stats['wins']:<12} {stats['draws']:<10} {win_rate:>6.1f}%")


def main():
    tournament = Group19Tournament()
    tournament.run_tournament()


if __name__ == "__main__":
    main()
