import copy

import numpy as np

from .simple_arithmetic_crossover import sa_crossover


def crossover(pool, crossover_probabilty, crosspoints, crossover_method, alpha):
    new_pool = []

    # because each crossover generates 2 offspring
    num_children = len(pool) // 2

    for _ in range(num_children):
        parent1 = np.random.choice(pool)
        parent2 = np.random.choice(pool)
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)

        num_cells = len(parent1.get_cells("non_fixed"))
        for i in range(num_cells):

            random_number = np.random.random()
            if random_number <= crossover_probabilty:
                if crossover_method == "simple_arithmetic":
                    sa_crossover(child1.get_cells("non_fixed")[i],
                                 child2.get_cells("non_fixed")[i],
                                 alpha)
                else:
                    pass
            print(random_number)
            print("parent 1:{}".format(parent1.get_cells("non_fixed")[i].pprint()))
            print("parent 2:{}".format(parent2.get_cells("non_fixed")[i].pprint()))
            print("child 1:{}".format(child1.get_cells("non_fixed")[i].pprint()))
            print("child 2:{}".format(child2.get_cells("non_fixed")[i].pprint()))
        new_pool.append(child1)
        new_pool.append(child2)

    print("len = {}".format(len(new_pool)))
    return new_pool