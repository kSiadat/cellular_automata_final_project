from matplotlib import image
from random import randint

from template import r_to_bool, t


time = 32
size = (2 * time) + 3
centre = (size - 1) // 2


# gets population of grid
def get_population(grid):
    return sum([sum(grid[x])  for x in range(size)])

# returns new cell state given neighbourhood and templates tha map to 1
def match(data, template):
    live = True
    for x in range(5):
        if data[x] != template[x]:
            live = False
    return live

# updates entire grid
def update(rule, grid):
    new = [[0  for y in range(size)]  for x in range(size)]
    for x in range(size):
        for y in range(size):
            data = [grid[x-1][y],
                    grid[x][(y+1)%size],
                    grid[(x+1)%size][y],
                    grid[x][y-1],
                    grid[x][y]]
            live = False
            for Z in rule:
                if match(data, Z):
                    live = True
                    break
            if live:
                new[x][y] = 1
    return new

# prints grid
def display(grid):
    for X in grid:
        print(X)
    print()

# runs complete simulation of rule, with option to output grid data
def complete(rule, evaluator, draw=False):
    rule = r_to_set(rule)
    t = 0
    grid = [[0  for y in range(size)]  for x in range(size)]
    grid[centre][centre] = 1
    history = [1]
    if draw:
        image.imsave(f"t_0.png", grid, cmap="gray", vmin=0, vmax=1)
    while t < time:
        grid = evaluator(rule, grid)
        history.append(get_population(grid))
        t += 1
        if draw:
            image.imsave(f"t_{t}.png", grid, cmap="gray", vmin=0, vmax=1)
    return history

# converts bit-array rule to list of templates that map to 1
def r_to_set(rule):
    new = [t[31-x]  for x, X in enumerate(rule)  if X]
    return new


if __name__ == "__main__":
    rule = 3546121493
    print(r_to_bool(rule))
    print(rule)
    history = complete(r_to_bool(rule), update, True)
    print(history)
    print([(size ** 2) - X  for X in history])
    print()
