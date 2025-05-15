from matplotlib import image
from random import randint
import sqlite3


# rotates a template
def rotate(template):
    return [template[3], template[0], template[1], template[2], template[4]]

# mirrors a template
def flip(template):
    return [template[2], template[1], template[0], template[3], template[4]]

# converts a bit-array to a number
def to_num(array):
    total = 0
    for x in range(len(array)):
        total += (2**(len(array)-1-x)) * array[x]
    return total

# converts a number to bit-array of length l
def to_bool(num, l):
    template = [0  for x in range(l)]
    for x in range(l):
        i = 2**(l-1-x)
        if i <= num:
            num -= i
            template[x] = 1
    return template

# converts a template to 5 bit-array
def t_to_bool(num):
    template = to_bool(num, 5)
    return template

# converts a complete rule to 32 bit-array
def r_to_bool(num):
    template = to_bool(num, 32)
    return template

# gets all rotational/mirror duplicates of a rule
def get_dupes(rule):
    dupe = [[0  for x in range(len(rule))]  for x in range(7)]
    for x in range(len(rule)):
        dupe[0][31-r1[31-x]] = rule[x]
        dupe[1][31-r2[31-x]] = rule[x]
        dupe[2][31-r3[31-x]] = rule[x]
        dupe[3][31-f0[31-x]] = rule[x]
        dupe[4][31-f1[31-x]] = rule[x]
        dupe[5][31-f2[31-x]] = rule[x]
        dupe[6][31-f3[31-x]] = rule[x]
    return dupe

# fills db table 'duplicate' with rules
def fill_db():
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    #cur.execute("CREATE TABLE duplicate (id INT UNSIGNED UNIQUE PRIMARY KEY, duplicate BOOL) WITHOUT ROWID;")
    #cur.execute("DELETE FROM duplicate;")
    for x in range(2**10):
        cur.execute(f"INSERT INTO duplicate (id, duplicate) VALUES ({x}, 0);")
        if (x + 1) % 2**5 == 0:
            con.commit()
            print(x + 1)
    con.commit()
    con.close()

# marks duplicates in 'duplicate' table
def mark_dupes():
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    count = 1
    for x in range(0, 2**10):
        dupe = cur.execute(f"SELECT duplicate FROM duplicate WHERE id={x//4};").fetchall()[0][0]
        dupe_bool = get_dupes(r_to_bool(x))
        dupe_num = list(set([to_num(X)  for X in dupe_bool]))
        dupe_num = [X  for X in dupe_num  if X>x]
        if len(dupe_num) > 0:
            condition = f"id={dupe_num[0]//4}"
            for y in range(1, len(dupe_num)):
                condition += f" or id={dupe_num[y]//4}"
            cur.execute(f"UPDATE duplicate SET duplicate=1 WHERE {condition};")
            con.commit()
        if (x + 4) % 2**5 == 0:
            print(count, x)
            count += 1

# dislays rotational/mirror equivalent of each template
def display_map():
    for x in range(limit):
        print(x, "-->", r1[x], "-->", r2[x], "-->", r3[x])
    print()
    for x in range(limit):
        print(x, "-->", f0[x], "-->", f1[x], "-->", f2[x], "-->", f3[x])
    print()

# gets set of unique complete rules
def get_distinct(quantity):
    distinct = []
    while len(distinct) < quantity:
        new = randint(0, (2**32) - 1)
        dupes = [new]#[to_num(X)  for X in get_dupes(r_to_bool(new))]
        valid = not (new in distinct)
        for X in dupes:
            if X in distinct:
                valid = False
        if valid:
            distinct.append(new)
    return distinct  

# makes copy of grid data in specified folder that is 3 times larger (for word)
def enlarge(path, scale):
    for p in range(33):
        data = image.imread(f"{path}/t_{p}.png")
        #data = image.imread(f"{path}.png")
        new = []
        for X in data:
            line = []
            for Y in X:
                for z in range(scale):
                    line.append(Y[0])
            for z in range(scale):
                new.append(line)
        image.imsave(f"{path}/big_t_{p}.png", new, cmap="gray", vmin=0, vmax=1)
        #image.imsave(f"{path}_big.png", new, cmap="gray", vmin=0, vmax=1)    

# takes a horizontal 1-d ca and layers it in to 1 image
def layer(path):
    new = []
    for p in range(33):
        data = image.imread(f"{path}/t_{p}.png")
        middle = [X[0]  for X in data[33]]
        new.append(middle)
    image.imsave(f"{path}/layer.png", new, cmap="gray", vmin=0, vmax=1)

# overlays each timestep of a ca
def overlay(path):
    total = [[0  for y in range(67)]  for x in range(67)]
    for p in range(33):
        data = image.imread(f"{path}/t_{p}.png")
        for x, X in enumerate(data):
            for y, Y in enumerate(X):
                total[x][y] += Y[0]
    image.imsave(f"{path}/composite.png", total, cmap="gray", vmin=0, vmax=1)


limit = 32
t = [t_to_bool(x)  for x in range(limit)]
r1 = [to_num(rotate(t[x]))  for x in range(limit)]
r2 = [to_num(rotate(t[x]))  for x in r1]
r3 = [to_num(rotate(t[x]))  for x in r2]
f0 = [to_num(flip(t[x]))  for x in range(limit)]
f1 = [to_num(rotate(t[x]))  for x in f0]
f2 = [to_num(rotate(t[x]))  for x in f1]
f3 = [to_num(rotate(t[x]))  for x in f2]

db_name = "rules.db"


if __name__ == "__main__":
    enlarge("_temp", 10)
