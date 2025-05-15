from matplotlib import image
from random import randint

from template import to_bool


time = 32
size = (2 * time) + 3
centre = (size - 1) // 2


# updates cell state given custom outer-totalistic rule
def evaluate(rule, border, centre):
    half = centre * 6
    total = sum(border)
    if (total == 4 and rule[half]) or (total == 3 and rule[half+1]) or (total == 2 and rule[half+2] and border[0] == border[2]) or (total == 2 and rule[half+3] and border[0] != border[2]) or (total == 1 and rule[half+4]) or (total == 0 and rule[half+5]):
        return 1
    return 0

# updates cell state given pure outer-totalistic rule
def evaluate2(rule, border, centre):
    half = centre * 5
    total = sum(border)
    if (total == 4 and rule[half]) or (total == 3 and rule[half+1]) or (total == 2 and rule[half+2]) or (total == 1 and rule[half+3]) or (total == 0 and rule[half+4]):
        return 1
    return 0

# updates cell state gicen totalistic rule
def evaluate3(rule, border, centre):
    total = sum(border) + centre
    return rule[5-total]

# gets neighbours of a cell
def neighbours(grid, x, y):
    n = x - 1
    e = (y + 1) % len(grid)
    s = (x + 1) % len(grid)
    w = y - 1
    return [grid[n][y], grid[x][e], grid[s][y], grid[x][w]]

# updates grid but limits update area by timestep (unused)
def step_constrained(rule, grid, t):
    new = [[0  for y in range(size)]  for x in range(size)]
    length = (2 * t) + 3
    start = (size - length) // 2
    for x in range(start, start + length):
        for y in range(start, start + length):
            new[x][y] = evaluate(rule, neighbours(grid, x, y), grid[x][y])
    return new

# updates grid
def step(rule, grid, evaluator):
    new = [[0  for y in range(size)]  for x in range(size)]
    for x in range(size):
        for y in range(size):
            new[x][y] = evaluator(rule, neighbours(grid, x, y), grid[x][y])
    return new

# runs complete simulaton of 1 rule given evaluator, can output grid data
def complete(rule, evaluator, draw=False):
    t = 0
    grid = [[0  for y in range(size)]  for x in range(size)]
    grid[centre][centre] = 1
    history = [1]
    if draw:
        image.imsave(f"t_0.png", grid, cmap="gray", vmin=0, vmax=1)
    while t < time:
        grid = step(rule, grid, evaluator)
        history.append(sum([sum(X)  for X in grid]))
        t += 1
        if draw:
            image.imsave(f"t_{t}.png", grid, cmap="gray", vmin=0, vmax=1)
    return history

# draws population graph given population sequence
def draw(history, name, width=1):
    graph = [[1 for y in range(len(history) * width)] for x in range(size**2)]
    for y in range(len(history)):
        for x in range(size**2):
            if x < history[y]:
                for z in range(width):
                    graph[(size**2)-x-1][(y*width)+z] = 0
    image.imsave(f"{name}.png", graph, cmap="gray", vmin=0, vmax=1)


if __name__ == "__main__":
    rule = 95#randint(0, 64-1)
    bits = 10
    print(rule, to_bool(rule, bits))
    history = complete(to_bool(rule, bits), evaluate2, True)
    draw(history, f"rule_{rule}", 100)
    print(history)
    print()
