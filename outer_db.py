import sqlite3
from math import ceil, floor, log
from os import listdir

from outer_simulation import complete, draw, evaluate, evaluate2, evaluate3
from simulation import complete as complete2, update
from template import get_distinct, to_bool


# totalistic
db_simple = "outer_ca_simple"
# pure outer-totalistic
db_base = "outer_ca_base"
# custom outer-totalistic
db_distinct = "outer_ca_distinct"
#complete
db_sample = "complete_ca"


#opens connection with db
def connect(db_name):
    con = sqlite3.connect(f"{db_name}.db")
    cur = con.cursor()
    return con, cur

# delete table(s)/contents of table(s) from db
def db_command(db_name, command, table):
    con, cur = connect(db_name)
    if command == "delete":
        for T in table:
            cur.execute(f"DELETE FROM {T};")
    elif command == "drop":
        for T in table:
            cur.execute(f"DROP TABLE {T};")
    con.close()

# create pre_sequence table
def create_pre_sequence(con, cur):
    txt = ""
    for x in range(10):
        txt += f", t0{x} UNSIGNED INT"
    for x in range(10, 33):
        txt += f", t{x} UNSIGNED INT"
    cur.execute(f"CREATE TABLE pre_sequence (rule UNSIGNED INT PRIMARY KEY{txt}) WITHOUT ROWID;")
    con.commit()

#create growth table
def create_growth(con, cur):
    cur.execute(f"CREATE TABLE growth (rule UNSIGNED INT PRIMARY KEY, up BOOL, flat BOOL, fall BOOL) WITHOUT ROWID;")
    con.commit()

# create filter table
def create_filter(con, cur):
    cur.execute(f"CREATE TABLE filter (rule UNSIGNED INT PRIMARY KEY, manual BOOL, auto BOOL, inverse BOOL, base INT, scale INT) WITHOUT ROWID;")
    con.commit()

# run simulation of ruleset, and store results in pre_sequence and growth as appropriate
def fill_pre_sequence(con, cur, rules, bits, simulator, evaluator):
    columns = "rule"
    for x in range(10):
        columns += f", t0{x}"
    for x in range(10, 33):
        columns += f", t{x}"
    for t, x in enumerate(rules):
        history = simulator(to_bool(x, bits), evaluator)
        up, flat, fall = check_growth(history)
        data = ", ".join([str(Y) for Y in history])
        cur.execute(f"INSERT INTO pre_sequence ({columns}) VALUES ({x}, {data});")
        cur.execute(f"INSERT INTO growth (rule, up, flat, fall) VALUES ({x}, {up}, {flat}, {fall});")
        if (t + 1) % 2**6 == 0:
            con.commit()
            print(t + 1)
    con.commit()

# match labels to rules based on if population sequence goes up/flat/down
def check_growth(history):
    up = False
    flat = (history[1] == history[0])
    fall = (history[1] < history[0])
    for x in range(2, len(history)):
        if history[x] > history[x-1]:
            up = True
        elif history[x] == history[x-1]:
            flat = True
        elif history[x] < history[x-1]:
            fall = True
    return up, flat, fall

# draw graphs for all rules where sequence goes up and down
def draw_complex(con, cur):
    res = cur.execute(f"SELECT (rule) FROM growth WHERE up=1 AND fall=1;")
    rules = ", ".join([str(X[0]) for X in res])
    res = cur.execute(f"SELECT * FROM pre_sequence WHERE rule IN ({rules});")
    for X in res:
        draw(X[1:], f"graph_{X[0]}", 100)

# draw graphs of all rules where sequence stays the same (unused)
def draw_flat(con, cur):
    res = cur.execute(f"SELECT (rule) FROM growth WHERE flat=1 AND fall=0;")
    rules = ", ".join([str(X[0]) for X in res])
    res = cur.execute(f"SELECT * FROM pre_sequence WHERE rule IN ({rules});")
    for X in res:
        draw(X[1:], f"graph_{X[0]}", 100)

# gets names of all rules that have graph in specified folder
def get_complex(addr):
    files = listdir(addr)
    rules = [int(X[6:-4]) for X in files]
    return rules

# sums bit-arrays of a set of rules
def get_total(rules, bits):
    total = [0 for x in range(bits)]
    for X in rules:
        arr = to_bool(X, bits)
        for y in range(bits):
            total[y] += arr[y]
    print(total)


# general function to create db tables, perform simulation, and store data
def simulate_db(db_name, rules, bits, simulator, evaluator):
    con, cur = connect(db_name)
    create_pre_sequence(con, cur)
    create_growth(con, cur)
    fill_pre_sequence(con, cur, rules, bits, simulator, evaluator)
    con.close()

# simulate_db for pure outer_totalistic
def simulate_base():
    simulate_db(db_base, range(2**10), 10, complete, evaluate2)

# simulate_db for custom outer_totalistic
def simulate_distinct():
    simulate_db(db_distinct, range(2**12), 12, complete, evaluate)

# simulate_db for complete
def simulate_sample():
    simulate_db(db_sample, get_distinct(4096), 32, complete2, update)

# simulate_db for totalistic
def simulate_simple():
    simulate_db(db_simple, range(2**6), 6, complete, evaluate3)


# general function to draw all 'complex' graphs
def draw_db(db_name):
    con, cur = connect(db_name)
    draw_complex(con, cur)
    con.close()

# draw_db for pure outer-totalistic
def draw_base():
    draw_db(db_base)

# draw_db for custom outer-totalistic
def draw_distinct():
    draw_db(db_distinct)

# draw_db for complete
def draw_sample():
    draw_db(db_sample)

# draw_db for totalistic
def draw_simple():
    draw_db(db_simple)


# checks if a population sequence matches the pattern with a specific base
def check_pattern(history, base):
    limit = floor(log(len(history), 2))-ceil(log(base, 2))
    scale = history[base] / history[0]
    if scale % 1 != 0:
        return False, scale
    for x in range(limit):
        offset = base * (2**x)
        for y in range(offset):
            if history[y] == 0:
                return False, scale
            if history[y+offset] / history[y] != scale:
                return False, scale
    return True, scale

# filters rules based on if they match the pattern. records lowest valid base
def filter_db(db_name):
    # checks all possible bases for a population sequence
    def check_bases(base, data, new, i=0):
        while base <= len(data[0][1]) // 2:
            for x in range(len(data)):
                if not new[x][1+i]:
                    pattern, scale = check_pattern(data[x][1], base)
                    new[x][1+i] = pattern
                    new[x][-2] = base
                    new[x][-1] = scale
            print(base)
            base += 1
        return new
    con, cur = connect(db_name)
    create_filter(con, cur)
    res = cur.execute(f"SELECT * FROM pre_sequence;")
    data = [[X[0], [Y  for Y in X[1:]]]  for X in res]
    new = [[X[0], False, False, 0, 0]  for X in data]
    new = check_bases(1, data, new)
    for x, X in enumerate(new):
        cur.execute(f"INSERT INTO filter (rule, auto, inverse, base, scale) VALUES ({X[0]}, {X[1]}, {X[2]}, {X[3]}, {X[4]});")
        if (x+1)%128 == 0:
            print(x+1)
    con.commit()
    con.close()

# filter_db for pure outer-totalistic
def filter_base():
    filter_db(db_base)

# filter_db for custom outer-totalistic
def filter_distinct():
    filter_db(db_distinct)

# filter_db for complete
def filter_sample():
    filter_db(db_sample)

#filter_db for totalistic
def filter_simple():
    filter_db(db_simple)


# gets sum of bit-array of rules in db.filter that match condition
def sum_rules(db_name, condition, bits):
    con, cur = connect(db_name)
    res = cur.execute(f"SELECT rule FROM filter WHERE auto=1 AND {condition};")
    data = [to_bool(X[0], bits)  for X in res]
    total = [0 for x in range(bits)]
    for X in data:
        for y in range(bits):
            total[y] += X[y]
    con.close()
    return total, len(data)

# sum_rules for totalistic
def sum_simple(condition):
    return sum_rules(db_simple, condition, 6)

# sum_rules for pure puter-totalistic
def sum_base(condition):
    return sum_rules(db_base, condition, 10)

# sum_rules for custom outer-totalistic
def sum_distinct(condition):
    return sum_rules(db_distinct, condition, 12)

# sum_rules for complete
def sum_sample(condition):
    return sum_rules(db_sample, condition, 32)

# prints population sequence of all rules in db.filter given condition
def get_sequence(db_name, condition):
    con, cur = connect(db_name)
    res = cur.execute(f"SELECT rule FROM filter WHERE auto=1 AND {condition};")
    data = tuple([X[0]  for X in res])
    print(data)
    res = cur.execute(f"SELECT * FROM pre_sequence WHERE rule in {data};")
    data = [X[1:]  for X in res]
    for X in data:
        print(X)
    con.close()

# get_sequence for totalistic
def get_sequence_simple(condition):
    get_sequence(db_simple, condition)

# get_sequence for pure outer-totalistic
def get_sequence_simple(condition):
    get_sequence(db_base, condition)

# get_sequence for custom outer-totalistic
def get_sequence_simple(condition):
    get_sequence(db_distinct, condition)

# get_sequence for complete
def get_sequence_simple(condition):
    get_sequence(db_complete, condition)


if __name__ == "__main__":
    pass
    #print(sum_distinct("base=2 and scale>1"))
