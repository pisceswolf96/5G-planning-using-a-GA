from ..network.net_funcs import distance, received_power


class Plan(object):
    """Representation of a single plan(cells + users)

    Attributes:
        _cell_list: List of all the cells in a given plan.
        _users: List of the users associated with the plan.
        _candidate_points: List of candidate points used by the plan.
        _fixed_macro_cells: List of fixed macro cells(inherited from 4G).
        _macro_cells: List of macro cells in the plan.
        _micro_cells: List of micro cells in the plan(can be empty).
        _pico_cells: List of pico cells in the plan(can be empty).
        _femto_cells: List of femto cells in the plan(can be empty).
        _cost: Cost in dollars.
        _fitness: Fitness of current plan.
        _connected_users: Number of connected users.
    """

    def __init__(
            self,
            cell_list,
            users,
            candidate_points,
            num_fixed_macro_cells,
            num_macro_cells,
            num_micro_cells=None,
            num_pico_cells=None,
            num_femto_cells=None):

        self._users = users
        self._candidate_points = candidate_points

        current_begin = 0
        current_end = num_fixed_macro_cells
        self._fixed_macro_cells = cell_list[current_begin: current_end]

        current_begin = current_end
        current_end = current_begin + num_macro_cells
        self._macro_cells = cell_list[current_begin: current_end]

        if num_micro_cells is not None:
            current_begin = current_end
            current_end = current_begin + num_micro_cells
            self._micro_cells = cell_list[current_begin: current_end]
        else:
            self._micro_cells = []

        if num_pico_cells is not None:
            current_begin = current_end
            current_end = current_begin + num_pico_cells
            self._pico_cells = cell_list[current_begin: current_end]
        else:
            self._pico_cells = []

        if num_femto_cells is not None:
            current_begin = current_end
            current_end = current_begin + num_femto_cells
            self._femto_cells = cell_list[current_begin: current_end]
        else:
            self._femto_cells = []

        self._cost = None
        self._fitness = None
        self._connected_users = None

    # getters
    def get_cells(self, cells_type="all"):
        """Returns a list of cells in the plan.

        Args:
            cells_type: A string of the desired cells
                      it accepts the following(
                          all,
                          non_fixed,
                          fixed_macro,
                          micro,
                          pico,
                          femto
                          ).
        """

        if cells_type == "all":
            cells = self._fixed_macro_cells + self._macro_cells + \
                self._micro_cells + self._pico_cells + self._femto_cells
        elif cells_type == "non_fixed":
            cells = self._macro_cells + self._micro_cells + \
                self._pico_cells + self._femto_cells
        elif cells_type == "fixed_macro":
            cells = self._fixed_macro_cells
        elif cells_type == "macro":
            cells = self._macro_cells
        elif cells_type == "micro":
            cells = self._micro_cells
        elif cells_type == "pico":
            cells = self._pico_cells
        elif cells_type == "femto":
            cells = self._femto_cells
        return cells

    def get_users(self):
        """Returns the list of users associated with the plan."""
        return self._users

    def get_num_of_connected_users(self):
        return self._connected_users

    def get_cost(self):
        return self._cost

    def get_fitness(self):
        return self._fitness

    def get_candidate_points(self):
        """Returns the list of candidate points."""
        return self._candidate_points

    def get_num_cells(self, cell_type="macro"):
        return len(self.get_cells(cell_type))

    # setters
    def connect_users(self):
        """Connect users of each plan in pool to available cellular cells."""
        for user in self.get_users():
            user.empty_close_bss()
            for cell in self.get_cells():
                # if user is within the radius of the cell
                if distance(user.get_xcoord(), user.get_ycoord(), cell.get_xcoord(),
                            cell.get_ycoord()) < cell.get_radius():
                    # if cell is available
                    if cell.is_available():
                        user.add_to_close_bss(cell)

            # if user is within at least one base station range
            if len(user.get_close_bss()):
                desired = user.get_close_bss()[0]
                for tested_cell in user.get_close_bss()[1:]:
                    dist1 = distance(desired.get_xcoord(),
                                     desired.get_ycoord(),
                                     user.get_xcoord(),
                                     user.get_ycoord())
                    dist2 = distance(tested_cell.get_xcoord(),
                                     tested_cell.get_ycoord(),
                                     user.get_xcoord(),
                                     user.get_ycoord())

                    num_bs = self.get_num_cells(desired.get_cell_type())
                    power1 = received_power(desired.get_power(),
                                            num_bs,
                                            dist1,
                                            desired.get_frequency(), 0, 0)

                    num_bs = self.get_num_cells(tested_cell.get_cell_type())
                    power2 = received_power(tested_cell.get_power(),
                                            num_bs,
                                            dist2,
                                            tested_cell.get_frequency(), 0, 0)

                    if power2 > power1:
                        desired = tested_cell
                user.set_connected_bs(desired)
                desired.add_user(user)

    def calculate_connected_users(self):
        """Calculate the number of connected users in the plan."""
        users = self.get_users()
        connected_users = 0

        for user in users:
            if user.is_connected():
                connected_users += 1
        self._connected_users = connected_users

    def calculate_cost(self):
        cost = 0
        for cell in self.get_cells():
            if cell.get_state():
                cost += cell.get_cost()
        self._cost = cost

    def disconnect_unneeded_cells(self):
        """Disconnect cells that don't have enough users to be active."""
        for cell in self.get_cells():
            cell.check_if_needed()

    def calculate_fitness(self):
        self._fitness = self._cost

    def operate(self):
        """Operate the plan, by doing the necessary operations."""
        self.connect_users()
        self.disconnect_unneeded_cells()
        self.calculate_connected_users()
        self.calculate_cost()
        self.calculate_fitness()

    def pprint(self):
        """Print the plan's attributes."""

        return """
        # of connected users: {} of {}
        fitness             : {}
        """.format(self.get_num_of_connected_users(),
                   len(self.get_users()),
                   self.get_fitness())
