import random
from collections import deque
import heapq


# YOUR OLD AGENT (keep this for reference)

class GreedyGridAgent:
    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)



# NEW AGENT FOR LAB 3 (ADD THIS)

class SearchAgent:
    def __init__(self, algorithm='BFS'):
        self.plan = []
        self.active_algorithm = algorithm
    
    # ---- BFS ----
    def bfs_search(self, start, goal, grid_size, walls):
        w, h = grid_size
        if start in walls or goal in walls:
            return None
        
        queue = deque()
        queue.append((start, []))
        visited = set()
        visited.add(start)
        
        while queue:
            pos, path = queue.popleft()
            if pos == goal:
                return path
            
            x, y = pos
            for nx, ny, action in [(x,y+1,'Up'), (x,y-1,'Down'), (x-1,y,'Left'), (x+1,y,'Right')]:
                if 0 <= nx < w and 0 <= ny < h:
                    new_pos = (nx, ny)
                    if new_pos not in walls and new_pos not in visited:
                        visited.add(new_pos)
                        queue.append((new_pos, path + [action]))
        return None
    
    # ---- DFS ----
    def dfs_search(self, start, goal, grid_size, walls):
        w, h = grid_size
        if start in walls or goal in walls:
            return None
        
        stack = [(start, [])]
        visited = set()
        visited.add(start)
        
        while stack:
            pos, path = stack.pop()
            if pos == goal:
                return path
            
            x, y = pos
            for nx, ny, action in [(x,y+1,'Up'), (x,y-1,'Down'), (x-1,y,'Left'), (x+1,y,'Right')]:
                if 0 <= nx < w and 0 <= ny < h:
                    new_pos = (nx, ny)
                    if new_pos not in walls and new_pos not in visited:
                        visited.add(new_pos)
                        stack.append((new_pos, path + [action]))
        return None
    
    # ---- UCS ----
    def ucs_search(self, start, goal, grid_size, walls):
        w, h = grid_size
        if start in walls or goal in walls:
            return None
        
        counter = 0
        heap = []
        heapq.heappush(heap, (0, counter, start, []))
        counter += 1
        best_cost = {start: 0}
        
        while heap:
            cost, _, pos, path = heapq.heappop(heap)
            if pos == goal:
                return path
            
            x, y = pos
            for nx, ny, action in [(x,y+1,'Up'), (x,y-1,'Down'), (x-1,y,'Left'), (x+1,y,'Right')]:
                if 0 <= nx < w and 0 <= ny < h:
                    new_pos = (nx, ny)
                    if new_pos not in walls:
                        new_cost = cost + 1
                        if new_pos not in best_cost or new_cost < best_cost[new_pos]:
                            best_cost[new_pos] = new_cost
                            heapq.heappush(heap, (new_cost, counter, new_pos, path + [action]))
                            counter += 1
        return None
    
    # ---- Find closest food ----
    def find_closest_food(self, pos, foods):
        if not foods:
            return None
        closest = None
        min_dist = float('inf')
        for food in foods:
            dist = abs(pos[0]-food[0]) + abs(pos[1]-food[1])
            if dist < min_dist:
                min_dist = dist
                closest = food
        return closest
    
    # ---- Main function ----
    def sense_and_act(self, percept):
        # If we have a plan, do next action
        if self.plan:
            return self.plan.pop(0)
        
        # Get info
        pos = tuple(percept['agent_pos'])
        foods = percept.get('all_food', [])
        grid = percept.get('grid_size', (10, 10))
        walls = set(percept.get('walls', []))
        
        if not foods:
            return 'Stay'
        
        goal = self.find_closest_food(pos, foods)
        if not goal:
            return 'Stay'
        
        # Run algorithm
        if self.active_algorithm == 'BFS':
            path = self.bfs_search(pos, goal, grid, walls)
        elif self.active_algorithm == 'DFS':
            path = self.dfs_search(pos, goal, grid, walls)
        elif self.active_algorithm == 'UCS':
            path = self.ucs_search(pos, goal, grid, walls)
        else:
            path = None
        
        if not path:
            return 'Stay'
        
        self.plan = path
        return self.plan.pop(0)