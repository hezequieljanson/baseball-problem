from collections import deque
# vizu
from graph_visualizer import draw_flow_network

class BaseballElimination:
    def __init__(self, filename):
        # Lê os dados do arquivo de entrada
        with open(filename, 'r') as f:
            self.n = int(f.readline().strip())  # Número de times
            self.teams = []                    # Lista com os nomes dos times
            self.wins = {}                     # Dicionário: time -> vitórias
            self.losses = {}                   # Dicionário: time -> derrotas
            self.remaining = {}                # Dicionário: time -> jogos restantes
            self.against = {}                  # Dicionário: time -> {adversário: jogos restantes contra}
            self.number_of_teams = 0

            lines = f.readlines()

            # Pega os nomes dos times
            for i in range(self.n):
                parts = lines[i].split()
                team = parts[0]
                self.teams.append(team)
            
            self.number_of_teams = len(self.teams)

            # Lê as estatísticas e confrontos
            for i in range(self.n):
                parts = lines[i].split()
                team = parts[0]
                self.wins[team] = int(parts[1])
                self.losses[team] = int(parts[2])
                self.remaining[team] = int(parts[3])
                self.against[team] = {}
                for j in range(self.n):
                    opponent = self.teams[j]
                    self.against[team][opponent] = int(parts[4 + j])

    def get_number_of_teams(self):
        return self.number_of_teams
    
    def get_teams(self):
        return self.teams
    
    def get_wins(self, team):
        if team not in self.teams:
            raise ValueError(f"Team '{team}' not found.")
        return self.wins[team]
    
    def get_losses(self, team):
        if team not in self.teams:
            raise ValueError(f"Team '{team}' not found.")
        return self.losses[team]
    
    def get_remaining(self, team):
        if team not in self.teams:
            raise ValueError(f"Team '{team}' not found.")
        return self.remaining[team]
    
    def get_against(self, team1, team2):
        if team1 not in self.teams or team2 not in self.teams:
            raise ValueError(f"One or both teams '{team1}' and '{team2}' not found.")
        return self.against[team1].get(team2, 0)

    def is_eliminated(self, team):
        if team not in self.teams:
            raise ValueError(f"Team '{team}' not found.")
        # Calcula o número máximo de vitórias que esse time pode atingir
        max_possible = self.wins[team] + self.remaining[team]
        # Monta o grafo de fluxo para checar eliminação por combinações de jogos
        graph, total_capacity = self.build_flow_network(team, max_possible)

        # Visualiza o grafo criado (opcional)
        draw_flow_network(graph, 'source', 'sink', team)

        # Aplica Ford-Fulkerson para calcular o fluxo máximo
        max_flow = self.ford_fulkerson(graph, 'source', 'sink')
        
        # Verifica eliminação trivial: outro time já tem mais vitórias
        for other in self.teams:
            if other != team and self.wins[other] > max_possible:
                return True

        # Se o fluxo não for suficiente para distribuir todos os jogos restantes, o time está eliminado
        return max_flow < total_capacity

    def certificate_of_elimination(self, team):
        # Calcula o número máximo de vitórias que o time pode alcançar
        max_possible = self.wins[team] + self.remaining[team]

        # Verifica se há eliminação trivial
        # Exemplo: alguém já tem mais vitórias do que o time pode alcançar
        trivial_eliminators = [other for other in self.teams if other != team and self.wins[other] > max_possible]
        if trivial_eliminators:
            return trivial_eliminators

        # Caso não seja trivial, constrói o grafo de fluxo e executa Ford-Fulkerson
        graph, _ = self.build_flow_network(team, max_possible)
        residual = self.build_residual_graph(graph)

        self.ford_fulkerson(residual, 'source', 'sink')

        # ✅ 3. Realiza uma DFS no grafo residual a partir da 'source'
        # para identificar o lado esquerdo do corte mínimo
        visited = set()
        self.dfs(residual, 'source', visited)

        # ✅ 4. Retorna apenas os times reais que estão do lado da 'source'
        # (eliminadores "culpados" pela eliminação)
        eliminators = sorted([t for t in self.teams if t != team and t in visited])

        return eliminators

    def build_flow_network(self, team, max_possible):
        graph = {}
        total_game_capacity = 0
        graph['source'] = {}  # Nó de origem
        graph['sink'] = {}    # Nó de destino

        # Cria nós para cada jogo entre dois times (excluindo o time analisado)
        for i in range(self.n):
            for j in range(i + 1, self.n):
                team_i = self.teams[i]
                team_j = self.teams[j]
                if team_i == team or team_j == team:
                    continue
                games_left = self.against[team_i][team_j]
                if games_left == 0:
                    continue

                game_node = f'{team_i}_{team_j}'  # Nome do nó de jogo
                graph['source'][game_node] = games_left  # Aresta da source para o nó de jogo
                total_game_capacity += games_left

                # Conecta nó do jogo aos dois times com capacidade infinita
                graph[game_node] = {team_i: float('inf'), team_j: float('inf')}

        # Conecta os times à sink com limite de vitórias que podem atingir sem eliminar o time atual
        for other in self.teams:
            if other == team:
                continue
            cap = max(0, max_possible - self.wins[other])
            graph.setdefault(other, {})['sink'] = cap

        return graph, total_game_capacity

    def build_residual_graph(self, graph):
        # Cria o grafo residual para fluxo reversível
        residual = {}
        for u in graph:
            residual.setdefault(u, {})
            for v in graph[u]:
                residual[u][v] = graph[u][v]       # Capacidade original
                residual.setdefault(v, {})
                residual[v].setdefault(u, 0)       # Capacidade reversa inicial zero
        return residual

    def bfs(self, residual, source, sink, parent):
        # Busca em largura para encontrar caminho aumentante
        visited = set()
        queue = deque([source])
        visited.add(source)

        while queue:
            u = queue.popleft()
            for v in residual[u]:
                if v not in visited and residual[u][v] > 0:
                    parent[v] = u
                    visited.add(v)
                    queue.append(v)
                    if v == sink:
                        return True
        return False

    def ford_fulkerson(self, graph, source, sink):
        # Algoritmo de Ford-Fulkerson para fluxo máximo
        residual = self.build_residual_graph(graph)
        parent = {}
        max_flow = 0

        # Enquanto encontrar caminho aumentante, envia fluxo
        while self.bfs(residual, source, sink, parent):
            path_flow = float('inf')
            s = sink
            while s != source:
                u = parent[s]
                path_flow = min(path_flow, residual[u][s])
                s = u

            # Atualiza capacidades do grafo residual
            v = sink
            while v != source:
                u = parent[v]
                residual[u][v] -= path_flow
                residual[v][u] += path_flow
                v = u

            max_flow += path_flow

        return max_flow

    def dfs(self, residual, node, visited):
        # DFS para descobrir nós alcançáveis da source no corte mínimo
        visited.add(node)
        for neighbor in residual.get(node, {}):
            if neighbor not in visited and residual[node][neighbor] > 0:
                self.dfs(residual, neighbor, visited)
