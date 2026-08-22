from agent import SearchAgent
import random
import tkinter as tk


# ==================================================
# GRID GAME ENVIRONMENT
# ==================================================

class VisualGridHuntGame:

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=0,
        custom_walls=None
    ):
        self.width = width
        self.height = height

        # Agent starting position
        self.agent_pos = [0, 0]

        # Walls
        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        # Food
        self.food_positions = set()

        while len(self.food_positions) < num_food:

            fx = random.randint(
                0,
                self.width - 1
            )

            fy = random.randint(
                0,
                self.height - 1
            )

            position = (fx, fy)

            if (
                position != (0, 0)
                and position not in self.walls
            ):
                self.food_positions.add(
                    position
                )

        # Opponents
        self.opponents = []

        while len(self.opponents) < num_opponents:

            ox = random.randint(
                0,
                self.width - 1
            )

            oy = random.randint(
                0,
                self.height - 1
            )

            position = (ox, oy)

            if (
                position != (0, 0)
                and position not in self.walls
                and position not in self.food_positions
                and position not in [
                    tuple(op)
                    for op in self.opponents
                ]
            ):
                self.opponents.append(
                    [ox, oy]
                )

        # Game information
        self.score = 0
        self.steps = 0
        self.collision = False

        # Toxic traps
        self.toxic_traps = set()
        self._initialize_toxic_traps()

    # --------------------------------------------------
    # INITIALIZE TOXIC TRAPS
    # --------------------------------------------------
    def _initialize_toxic_traps(self):

        valid_positions = []

        opponent_positions = {
            tuple(op)
            for op in self.opponents
        }

        for x in range(self.width):
            for y in range(self.height):

                pos = (x, y)

                if (
                    pos != (0, 0)
                    and pos not in self.walls
                    and pos not in self.food_positions
                    and pos not in opponent_positions
                ):
                    valid_positions.append(
                        pos
                    )

        number_of_traps = min(
            3,
            len(valid_positions)
        )

        if number_of_traps > 0:
            self.toxic_traps = set(
                random.sample(
                    valid_positions,
                    number_of_traps
                )
            )

    # --------------------------------------------------
    # GET PERCEPT
    # --------------------------------------------------
    def get_percept(self):

        return {
            'agent_pos': list(
                self.agent_pos
            ),

            'grid_size': (
                self.width,
                self.height
            ),

            'walls': list(
                self.walls
            ),

            'all_food': list(
                self.food_positions
            ),

            # Extra environment information
            'toxic_traps': list(
                self.toxic_traps
            ),

            'opponent_positions': [
                list(op)
                for op in self.opponents
            ],

            'remaining_food': len(
                self.food_positions
            ),

            'score': self.score,

            'collision': self.collision
        }

    # --------------------------------------------------
    # EXECUTE ACTION
    # --------------------------------------------------
    def execute_action(self, action):

        self.steps += 1

        new_pos = list(
            self.agent_pos
        )

        if action == 'Up':

            new_pos[1] = min(
                self.height - 1,
                new_pos[1] + 1
            )

        elif action == 'Down':

            new_pos[1] = max(
                0,
                new_pos[1] - 1
            )

        elif action == 'Left':

            new_pos[0] = max(
                0,
                new_pos[0] - 1
            )

        elif action == 'Right':

            new_pos[0] = min(
                self.width - 1,
                new_pos[0] + 1
            )

        # Wall collision
        if tuple(new_pos) in self.walls:

            self.score -= 5

        else:

            self.agent_pos = new_pos

        current_pos = tuple(
            self.agent_pos
        )

        # Eat food
        if current_pos in self.food_positions:

            self.food_positions.remove(
                current_pos
            )

            self.score += 20

            # Important:
            # Clear the old search plan because
            # the target food has been eaten.
            # The agent will calculate a new path.
            # This is handled naturally because
            # the plan becomes empty after execution.

        # Toxic trap
        if current_pos in self.toxic_traps:

            self.score -= 15

            print(
                "Stepped on toxic trap! "
                f"Score: {self.score}"
            )

        # Move opponents
        for op in self.opponents:

            move = random.choice([
                'Up',
                'Down',
                'Left',
                'Right',
                'Stay'
            ])

            possible_position = list(op)

            if move == 'Up':

                possible_position[1] = min(
                    self.height - 1,
                    possible_position[1] + 1
                )

            elif move == 'Down':

                possible_position[1] = max(
                    0,
                    possible_position[1] - 1
                )

            elif move == 'Left':

                possible_position[0] = max(
                    0,
                    possible_position[0] - 1
                )

            elif move == 'Right':

                possible_position[0] = min(
                    self.width - 1,
                    possible_position[0] + 1
                )

            # Opponents cannot move into walls
            if (
                tuple(possible_position)
                not in self.walls
            ):
                op[:] = possible_position

            # Check collision
            if op == self.agent_pos:

                self.score -= 50
                self.collision = True

    # --------------------------------------------------
    # CHECK GAME END
    # --------------------------------------------------
    def is_done(self):

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )


# ==================================================
# GUI
# ==================================================

class GridGameGUI:

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=10,
        num_opponents=0,
        walls=None,
        agent_algorithm='AStar'
    ):

        self.root = root

        self.root.title(
            "IT3012 - A* Grid Hunt"
        )

        # Environment
        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )

        # Search agent
        self.agent = SearchAgent(
            algorithm=agent_algorithm
        )

        # Canvas size
        max_canvas_dimension = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dimension // width,
                max_canvas_dimension // height
            )
        )

        canvas_width = (
            width
            * self.cell_size
        )

        canvas_height = (
            height
            * self.cell_size
        )

        self.canvas = tk.Canvas(
            root,
            width=canvas_width,
            height=canvas_height,
            bg="white"
        )

        self.canvas.pack()

        # Information label
        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial", 14)
        )

        self.label.pack(
            pady=10
        )

        # Start button
        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Arial", 12)
        )

        self.btn.pack(
            pady=5
        )

        self.draw_grid()

    # --------------------------------------------------
    # DRAW GRID
    # --------------------------------------------------
    def draw_grid(self):

        self.canvas.delete("all")

        # Draw cells and walls
        for x in range(self.env.width):

            for y in range(self.env.height):

                x1 = (
                    x
                    * self.cell_size
                )

                y1 = (
                    self.env.height - 1 - y
                ) * self.cell_size

                x2 = (
                    x1
                    + self.cell_size
                )

                y2 = (
                    y1
                    + self.cell_size
                )

                if (
                    x,
                    y
                ) in self.env.walls:

                    color = "gray"

                else:

                    color = "white"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="black"
                )

        # Draw walls
        for wx, wy in self.env.walls:

            x1 = (
                wx
                * self.cell_size
            )

            y1 = (
                self.env.height - 1 - wy
            ) * self.cell_size

            self.canvas.create_text(
                x1 + self.cell_size / 2,
                y1 + self.cell_size / 2,
                text="W",
                font=("Arial", 10, "bold")
            )

        # Draw toxic traps
        for tx, ty in self.env.toxic_traps:

            x1 = (
                tx
                * self.cell_size
            )

            y1 = (
                self.env.height - 1 - ty
            ) * self.cell_size

            self.canvas.create_oval(
                x1 + 5,
                y1 + 5,
                x1 + self.cell_size - 5,
                y1 + self.cell_size - 5,
                fill="purple"
            )

            self.canvas.create_text(
                x1 + self.cell_size / 2,
                y1 + self.cell_size / 2,
                text="T",
                fill="white"
            )

        # Draw food
        for fx, fy in self.env.food_positions:

            x1 = (
                fx
                * self.cell_size
            )

            y1 = (
                self.env.height - 1 - fy
            ) * self.cell_size

            self.canvas.create_oval(
                x1 + 10,
                y1 + 10,
                x1 + self.cell_size - 10,
                y1 + self.cell_size - 10,
                fill="orange"
            )

        # Draw opponents
        for ox, oy in self.env.opponents:

            x1 = (
                ox
                * self.cell_size
            )

            y1 = (
                self.env.height - 1 - oy
            ) * self.cell_size

            self.canvas.create_rectangle(
                x1 + 8,
                y1 + 8,
                x1 + self.cell_size - 8,
                y1 + self.cell_size - 8,
                fill="red"
            )

        # Draw agent
        ax, ay = self.env.agent_pos

        x1 = (
            ax
            * self.cell_size
        )

        y1 = (
            self.env.height - 1 - ay
        ) * self.cell_size

        self.canvas.create_oval(
            x1 + 5,
            y1 + 5,
            x1 + self.cell_size - 5,
            y1 + self.cell_size - 5,
            fill="blue"
        )

    # --------------------------------------------------
    # RUN GAME
    # --------------------------------------------------
    def run_loop(self):

        self.btn.config(
            state="disabled"
        )

        def step():

            if not self.env.is_done():

                percept = (
                    self.env.get_percept()
                )

                action = (
                    self.agent.sense_and_act(
                        percept
                    )
                )

                self.env.execute_action(
                    action
                )

                self.draw_grid()

                self.label.config(
                    text=(
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Action: {action}"
                    )
                )

                self.root.after(
                    250,
                    step
                )

            else:

                if self.env.collision:

                    end_text = (
                        "Collision! Game Over! "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                else:

                    end_text = (
                        "Finished! "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                self.label.config(
                    text=end_text
                )

                self.btn.config(
                    state="normal"
                )

        step()


# ==================================================
# MAIN PROGRAM
# ==================================================

if __name__ == "__main__":

    root = tk.Tk()

    # Run A* Search
    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=10,
        num_opponents=0,
        agent_algorithm='AStar'
    )

    root.mainloop()


