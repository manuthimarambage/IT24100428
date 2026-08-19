import random


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""
    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept['agent_pos']
        return random.choice(self.actions_pool)


# ---------------- Practical 2 ----------------

class SimpleReflexAgent:
    """Step 1.2: Stateless agent - pure Condition-Action (IF-THEN) rules.
    No __init__ override, no memory. This is exactly why it gets stuck in loops."""
    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            return 'Right'          # eat / keep moving
        elif percept['wall_ahead']:
            return 'Left'           # turn away from wall
        else:
            return 'Right'          # default: keep moving right


class ModelBasedAgent:
    """Step 1.3: Keeps internal memory (last_action) so it doesn't repeat
    the same failed move twice - lets it escape a loop the SimpleReflexAgent
    would get stuck in."""
    def __init__(self):
        self.last_action = None
        self.turn_options = ['Left', 'Down', 'Right', 'Up']

    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            action = 'Right'
        elif percept['wall_ahead']:
            if self.last_action in self.turn_options:
                idx = self.turn_options.index(self.last_action)
                action = self.turn_options[(idx + 1) % len(self.turn_options)]
            else:
                action = 'Left'
        else:
            action = 'Right'

        self.last_action = action
        return action


class SearchAgent:
    """Placeholder - real BFS implementation comes in Practical 3.
    Kept here only so 'from agent import ... SearchAgent' doesn't crash today."""
    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        return None