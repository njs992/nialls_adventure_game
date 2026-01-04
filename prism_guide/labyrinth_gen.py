import random
import curses

LABYRINTH_SIZE = 6

def _rc(idx, size=LABYRINTH_SIZE):
    return divmod(idx, size)

def _idx(r, c, size=LABYRINTH_SIZE):
    return r * size + c

def _roll(d, times=1):
    return sum(random.randint(1, d) for _ in range(times))

def generate_room_map(size=LABYRINTH_SIZE, seed=None):
    # seed: reproducible if provided, otherwise seed from OS entropy
    if seed is None:
        random.seed()
    else:
        random.seed(seed)

    N = size * size

    def build_one_layout():
        # pick special rooms (centers): dead end E, sealed entrance S, exit X
        all_idxs = list(range(N))
        specials = {}
        chosen = set()
        for key in ('E','S','X'):
            pick = random.choice([i for i in all_idxs if i not in chosen])
            specials[key] = [pick]
            chosen.add(pick)

        # remaining indices
        remaining = [i for i in all_idxs if i not in chosen]
        # exactly 6 rooms with 3 doors (no rooms with 4 doors)
        three_doors = set(random.sample(remaining, 6))
        remaining2 = [i for i in remaining if i not in three_doors]
        two_doors = set(remaining2)  # rest -> 2 doors

        # target normal-door counts (special centers E/S/X have 1; L handled as wall doors)
        target = [0] * N
        for i in specials['E'] + specials['S'] + specials['X']:
            target[i] = 1
        for i in three_doors:
            target[i] = 3
        for i in two_doors:
            target[i] = 2

        # adjacency pairs (only internal)
        neighbors = {}
        for idx in range(N):
            r, c = _rc(idx, size)
            neigh = []
            if r > 0: neigh.append(_idx(r-1, c, size))
            if r < size-1: neigh.append(_idx(r+1, c, size))
            if c > 0: neigh.append(_idx(r, c-1, size))
            if c < size-1: neigh.append(_idx(r, c+1, size))
            neighbors[idx] = neigh

        # try to build a consistent undirected door graph matching targets
        def build_edges():
            edges = set()
            deg = [0]*N
            order = list(range(N))
            random.shuffle(order)
            tries = 0
            while any(deg[i] < target[i] for i in range(N)):
                progress = False
                random.shuffle(order)
                for i in order:
                    while deg[i] < target[i]:
                        possible = [j for j in neighbors[i] if deg[j] < target[j] and (min(i,j), max(i,j)) not in edges]
                        if not possible:
                            break
                        j = random.choice(possible)
                        edges.add((min(i,j), max(i,j)))
                        deg[i] += 1
                        deg[j] += 1
                        progress = True
                if not progress:
                    tries += 1
                    if tries > 10:
                        return None
                    edges = set()
                    deg = [0]*N
                    random.shuffle(order)
            return edges

        edges = build_edges()
        if edges is None:
            # fallback: allow approximate satisfaction by greedy filling
            edges = set()
            deg = [0]*N
            pairs = [(i,j) for i in range(N) for j in neighbors[i] if i<j]
            random.shuffle(pairs)
            for i,j in pairs:
                if deg[i] < target[i] and deg[j] < target[j]:
                    edges.add((i,j)); deg[i]+=1; deg[j]+=1

        # Post-process: ensure no non-special room has exactly one standard door
        specials_idxs = set(sum(specials.values(), []))
        def fix_single_doors(edges):
            deg = [0]*N
            for a,b in edges:
                deg[a]+=1; deg[b]+=1
            tries = 0
            while any(deg[i]==1 and i not in specials_idxs for i in range(N)) and tries < 1000:
                for i in range(N):
                    if i in specials_idxs or deg[i] != 1:
                        continue
                    neighs = [j for j in neighbors[i] if (min(i,j),max(i,j)) not in edges]
                    random.shuffle(neighs)
                    for j in neighs:
                        # avoid creating >3-degree non-special rooms; don't connect to specials
                        if j in specials_idxs:
                            continue
                        if deg[i] >= 3 or deg[j] >= 3:
                            continue
                        edges.add((min(i,j), max(i,j)))
                        deg[i]+=1; deg[j]+=1
                        break
                tries += 1
            return edges

        edges = fix_single_doors(edges)

        # ensure open passages do NOT touch special centers (specials must have a real door)
        candidate_edges_for_open = [e for e in edges if e[0] not in sum(specials.values(), []) and e[1] not in sum(specials.values(), [])]
        open_passages = set(random.sample(candidate_edges_for_open, min(8, len(candidate_edges_for_open))))

        # pick 2 loop-doors from existing normal edges (they remain edges but are visually 'L' on the wall)
        # choose two loop edges whose endpoint rooms do not overlap (one visual "L" per loop edge)
        loop_edges = set()
        edges_list = list(edges)
        random.shuffle(edges_list)
        for a,b in edges_list:
            if len(loop_edges) >= 2:
                break
            used = set(x for ed in loop_edges for x in ed)
            if a in used or b in used:
                continue
            loop_edges.add((a,b))
        # fallback: try to find any disjoint pair of edges
        if len(loop_edges) < 2 and len(edges_list) >= 2:
            from itertools import combinations
            pairs = list(combinations(edges_list, 2))
            random.shuffle(pairs)
            found = False
            for e1,e2 in pairs:
                a1,b1 = e1; a2,b2 = e2
                used = {a1,b1,a2,b2}
                if len(used) == 4:
                    loop_edges = {e1, e2}
                    found = True
                    break
            # if none found, leave loop_edges empty -> will fail validation and trigger regeneration

        # build horizontal and vertical door maps
        horiz = [[False]*size for _ in range(size-1)]  # between r and r+1 at column c
        vert = [[False]*(size-1) for _ in range(size)]  # between c and c+1 at row r
        horiz_open = [[False]*size for _ in range(size-1)]
        vert_open = [[False]*(size-1) for _ in range(size)]
        horiz_loop_edge = [[False]*size for _ in range(size-1)]
        vert_loop_edge = [[False]*(size-1) for _ in range(size)]
        for a,b in edges:
            ra,ca = _rc(a,size); rb,cb = _rc(b,size)
            if ra == rb:
                r = ra; c = min(ca,cb)
                vert[r][c] = True
                if (a,b) in open_passages or (b,a) in open_passages:
                    vert_open[r][c] = True
                if (a,b) in loop_edges or (b,a) in loop_edges:
                    vert_loop_edge[r][c] = True
            else:
                r = min(ra,rb); c = ca
                horiz[r][c] = True
                if (a,b) in open_passages or (b,a) in open_passages:
                    horiz_open[r][c] = True
                if (a,b) in loop_edges or (b,a) in loop_edges:
                    horiz_loop_edge[r][c] = True

        # compute per-room loop marker position (one marker per room max), avoid placing on same side as a door/open passage
        loop_pos = [[None]*size for _ in range(size)]  # 'left','right','up','down' or None
        def try_place_loop_for_room(r,c, preferred_side):
            # don't overwrite existing marker
            if loop_pos[r][c] is not None:
                return
            # sides and checks
            sides = ['up','right','down','left']
            # rotate so preferred is first
            while sides[0] != preferred_side:
                sides = sides[1:]+[sides[0]]
            for side in sides:
                # skip if outside map
                if side == 'up' and r==0: continue
                if side == 'down' and r==size-1: continue
                if side == 'left' and c==0: continue
                if side == 'right' and c==size-1: continue
                # if there's a door or open passage on that side, skip
                blocked = False
                if side == 'left':
                    if c>0 and (vert[r][c-1] or vert_open[r][c-1]): blocked = True
                if side == 'right':
                    if c < size-1 and (vert[r][c] or vert_open[r][c]): blocked = True
                if side == 'up':
                    if r>0 and (horiz[r-1][c] or horiz_open[r-1][c]): blocked = True
                if side == 'down':
                    if r < size-1 and (horiz[r][c] or horiz_open[r][c]): blocked = True
                if not blocked:
                    loop_pos[r][c] = side
                    return

        # place exactly one 'L' marker for each loop edge (choose one endpoint to show the marker)
        for a,b in list(loop_edges):
            # pick which endpoint will display the loop marker
            if random.choice([True, False]):
                show, other = a, b
            else:
                show, other = b, a
            rshow, cshow = _rc(show, size)
            rother, cother = _rc(other, size)
            if rshow == rother:
                preferred = 'right' if cother > cshow else 'left'
            else:
                preferred = 'down' if rother > rshow else 'up'
            # try to place on the chosen endpoint; if blocked, try the other endpoint
            try_place_loop_for_room(rshow, cshow, preferred)
            if loop_pos[rshow][cshow] is None:
                # try the opposite endpoint with its preferred side
                if rshow == rother:
                    pref2 = 'right' if cshow > cother else 'left'
                else:
                    pref2 = 'down' if rshow > rother else 'up'
                try_place_loop_for_room(rother, cother, pref2)

        # compute enemies and treasures per room
        def room_loot(idx):
            # special center features
            feat = None
            if idx in specials['E']: feat='E'
            elif idx in specials['S']: feat='S'
            elif idx in specials['X']: feat='X'

            r,c = _rc(idx,size)
            # any open passage touching this room?
            has_open = False
            if c>0 and vert_open[r][c-1]: has_open = True
            if c < size-1 and vert_open[r][c]: has_open = True
            if r>0 and horiz_open[r-1][c]: has_open = True
            if r < size-1 and horiz_open[r][c]: has_open = True

            if feat in ('E','S','X'):
                enemies = 0
                treasure = 1 if (feat=='E' or random.random() < 0.10) else 0
            else:
                if has_open:
                    enemies = max(0, _roll(4,3) - 10)
                else:
                    enemies = max(0, _roll(4,3) - 8)
                treasure = 0
                if random.random() < 0.05:
                    treasure = 1
            return enemies, treasure, feat

        room_info = [room_loot(i) for i in range(N)]

        return {
            'specials': specials,
            'edges': edges,
            'open_passages': open_passages,
            'loop_edges': loop_edges,
            'horiz': horiz, 'vert': vert,
            'horiz_open': horiz_open, 'vert_open': vert_open,
            'horiz_loop_edge': horiz_loop_edge, 'vert_loop_edge': vert_loop_edge,
            'loop_pos': loop_pos,
            'room_info': room_info,
            'neighbors': neighbors
        }

    def validate_layout(layout):
        specials = layout['specials']
        edges = layout['edges']
        open_passages = layout['open_passages']
        loop_edges = layout['loop_edges']
        neighbors = layout['neighbors']

        deg = [0]*N
        for a,b in edges:
            deg[a]+=1; deg[b]+=1

        # Test 1: non-special rooms must have 2 or 3 door-like features
        special_idxs = set(sum(specials.values(), []))
        for i in range(N):
            if i in special_idxs:
                continue
            if deg[i] not in (2,3):
                return False

        # Test 2: connectivity
        adj = {i:set() for i in range(N)}
        for a,b in edges:
            if (a,b) in loop_edges or (b,a) in loop_edges:
                continue
            adj[a].add(b); adj[b].add(a)
        loop_list = list(loop_edges)

        # New test: there must be exactly 2 loop-doors
        if len(loop_list) != 2:
            return False

        # New test: there must be exactly two 'L' markers placed (one per loop edge)
        lp = layout.get('loop_pos', None)
        if lp is None:
            return False
        marker_count = sum(1 for r in range(size) for c in range(size) if lp[r][c] is not None)
        if marker_count != 2:
            return False

        (a1,b1),(a2,b2) = loop_list
        # fully connect endpoints across loop pair
        for x in (a1,b1):
            for y in (a2,b2):
                adj[x].add(y)
                adj[y].add(x)

        # BFS from room 0
        start = 0
        seen = {start}
        stack = [start]
        while stack:
            cur = stack.pop()
            for nb in adj[cur]:
                if nb not in seen:
                    seen.add(nb); stack.append(nb)
        if len(seen) != N:
            return False

        return True

    # Try until a valid layout is produced (no retry limit)
    final_layout = None
    valid = False
    attempt = 0
    while True:
        attempt += 1
        layout = build_one_layout()
        if validate_layout(layout):
            final_layout = layout
            valid = True
            break
    if final_layout is None:
        final_layout = layout  # last attempt even if invalid

    # report validation result before printing the map
    # print("MAP PASSED TESTS" if valid else "MAP FAILED TESTS")
    
    # -----------------------
    # Regenerate enemies/treasure (layout fixed) until constraints met
    # Constraints:
    #  - total enemies between 36 and 50 inclusive
    #  - dead end ('E') must have at least 1 treasure
    #  - total treasures between 5 and 8 inclusive
    # Retry up to 5 times, increasing odds each retry
    def regen_loot_for_layout(layout, size, max_retries=25):
        N = size * size
        specials = layout['specials']
        horiz_open = layout['horiz_open']; vert_open = layout['vert_open']
        # helper to check if room has open passage
        def room_has_open(idx):
            r,c = _rc(idx, size)
            if c>0 and vert_open[r][c-1]: return True
            if c < size-1 and vert_open[r][c]: return True
            if r>0 and horiz_open[r-1][c]: return True
            if r < size-1 and horiz_open[r][c]: return True
            return False

        dead_idx = specials['E'][0]
        for attempt in range(max_retries):
            enemy_boost = attempt  # increases enemies chance by lowering subtraction
            treasure_boost = 0.05 * attempt
            room_info = []
            for idx in range(N):
                feat = None
                if idx in specials['E']: feat='E'
                elif idx in specials['S']: feat='S'
                elif idx in specials['X']: feat='X'
                has_open = room_has_open(idx)
                if feat in ('E','S','X'):
                    enemies = 0
                    base_chance = 0.10 if feat in ('S','X') else 1.0
                    treasure = 1 if (feat=='E' or random.random() < (base_chance + treasure_boost)) else 0
                else:
                    roll = _roll(4,3)
                    sub = (10 - enemy_boost) if has_open else (8 - enemy_boost)
                    enemies = max(0, roll - sub)
                    treasure = 1 if random.random() < (0.05 + treasure_boost) else 0
                room_info.append((enemies, treasure, feat))

            # enforce dead-end treasure
            if room_info[dead_idx][1] == 0:
                e,t,f = room_info[dead_idx]
                room_info[dead_idx] = (e, 1, f)

            total_enemies = sum(e for e,_,_ in room_info)
            total_treasures = sum(t for _,t,_ in room_info)
            if 36 <= total_enemies <= 50 and 5 <= total_treasures <= 8:
                return room_info, True, attempt+1
        return room_info, False, max_retries

    loot_info, loot_ok, loot_attempts = regen_loot_for_layout(final_layout, size, max_retries=25)
    final_layout['room_info'] = loot_info
    # optional report
    # print(f"LOOT PASSED TESTS" if loot_ok else f"LOOT FAILED TESTS after {loot_attempts} attempts")

    return final_layout

def interactive_map(stdscr, layout, size):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  # walls
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # L
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)   # E S X
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # numbers
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW) # player highlight
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLUE)   # blue highlight
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_RED)    # boss highlight

    specials = layout['specials']
    player_pos = specials['S'][0]
    boss_pos = specials['E'][0]
    selected = 'player'
    blue_highlights = set()
    blink_state = True

    edges = layout['edges']
    loop_edges = layout['loop_edges']
    loop_pos = layout['loop_pos']

    # compute loop marker positions and targets
    loop_marker_to_target = {}
    loop_edges_list = list(loop_edges)
    if len(loop_edges_list) == 2:
        edge1, edge2 = loop_edges_list
        a1, b1 = edge1
        a2, b2 = edge2
        
        # Find which endpoint has the marker for each edge
        r_a1, c_a1 = _rc(a1, size)
        r_b1, c_b1 = _rc(b1, size)
        r_a2, c_a2 = _rc(a2, size)
        r_b2, c_b2 = _rc(b2, size)
        
        marker1_idx = a1 if loop_pos[r_a1][c_a1] is not None else b1
        marker2_idx = a2 if loop_pos[r_a2][c_a2] is not None else b2
        
        loop_marker_to_target[marker1_idx] = marker2_idx
        loop_marker_to_target[marker2_idx] = marker1_idx

    room_info = layout['room_info'][:]

    cell_w = 7
    pad_line = " " * cell_w
    def pad_with(text):
        return text.center(cell_w)

    def horiz_wall_segment(has_wall, has_door=False, door_char='D'):
        if not has_wall:
            return " " * cell_w
        if has_door:
            left = cell_w // 2
            right = cell_w - left - 1
            return "─" * left + door_char + "─" * right
        return "─" * cell_w

    def cell_text(idx):
        enemies, treasure, feat = room_info[idx]
        e = str(enemies)
        t = str(treasure)
        center = feat if feat is not None else ' '
        e = e[-1] if len(e) > 1 else e
        t = t[-1] if len(t) > 1 else t
        return f"{e}{center}{t}"

    def get_attr(ch, idx, pos_in_mid):
        base_attr = 0
        if ch in "┌┐└┘┬┴┼├┤─│":
            base_attr = curses.color_pair(1)
        elif ch == 'L':
            base_attr = curses.color_pair(2)
        elif ch in 'ESX':
            base_attr = curses.color_pair(3)
        elif ch in '0123456789 ':
            base_attr = curses.color_pair(4)
        else:
            base_attr = curses.color_pair(4)

        # highlights
        if pos_in_mid == 3:  # treasure position
            if idx == player_pos and (selected != 'player' or blink_state):
                base_attr = curses.color_pair(5)
        if pos_in_mid == 2:  # center
            if idx in blue_highlights:
                base_attr = curses.color_pair(6)
            if idx == boss_pos and (selected != 'boss' or blink_state):
                base_attr = curses.color_pair(7)

        return base_attr

    def draw_map():
        height, width = stdscr.getmaxyx()
        stdscr.clear()
        y = 0
        top_border = "┌" + (("─" * cell_w) + "┬") * (size - 1) + ("─" * cell_w) + "┐"
        for i, ch in enumerate(top_border):
            stdscr.addch(y, i, ch, curses.color_pair(1))
        y += 1

        for r in range(size):
            top_parts = []
            mid_parts = []
            bot_parts = []
            for c in range(size):
                idx = _idx(r, c, size)
                txt = cell_text(idx)
                mid = pad_with(txt)
                top = pad_line
                bot = pad_line

                lp = loop_pos[r][c]
                if lp == 'right':
                    mid = mid[:-1] + "L"
                elif lp == 'left':
                    mid = "L" + mid[1:]
                elif lp == 'down':
                    bot = bot[:cell_w//2] + "L" + bot[cell_w//2+1:]
                elif lp == 'up':
                    top = top[:cell_w//2] + "L" + top[cell_w//2+1:]

                top_parts.append(top)
                mid_parts.append(mid)
                bot_parts.append(bot)

            # top interior line
            x = 0
            stdscr.addch(y, x, "│", curses.color_pair(1))
            x += 1
            for c in range(size):
                for p, ch in enumerate(top_parts[c]):
                    attr = get_attr(ch, _idx(r, c, size), -1)  # not mid
                    stdscr.addch(y, x, ch, attr)
                    x += 1
                if c < size - 1:
                    sep = " " if layout['vert_open'][r][c] else "│"
                    stdscr.addch(y, x, sep, curses.color_pair(1))
                    x += 1
            stdscr.addch(y, x, "│", curses.color_pair(1))
            y += 1

            # middle content line
            x = 0
            stdscr.addch(y, x, "│", curses.color_pair(1))
            x += 1
            for c in range(size):
                idx = _idx(r, c, size)
                for p, ch in enumerate(mid_parts[c]):
                    attr = get_attr(ch, idx, p)
                    stdscr.addch(y, x, ch, attr)
                    x += 1
                if c < size - 1:
                    if layout['vert_open'][r][c]:
                        sep = " "
                    elif layout['vert'][r][c]:
                        sep = "D"
                    else:
                        sep = "│"
                    stdscr.addch(y, x, sep, curses.color_pair(1))
                    x += 1
            stdscr.addch(y, x, "│", curses.color_pair(1))
            y += 1

            # bottom interior line
            x = 0
            stdscr.addch(y, x, "│", curses.color_pair(1))
            x += 1
            for c in range(size):
                for p, ch in enumerate(bot_parts[c]):
                    attr = get_attr(ch, _idx(r, c, size), -1)
                    stdscr.addch(y, x, ch, attr)
                    x += 1
                if c < size - 1:
                    sep = " " if layout['vert_open'][r][c] else "│"
                    stdscr.addch(y, x, sep, curses.color_pair(1))
                    x += 1
            stdscr.addch(y, x, "│", curses.color_pair(1))
            y += 1

            # horizontal divider
            if r < size - 1:
                x = 0
                stdscr.addch(y, x, "├", curses.color_pair(1))
                x += 1
                for c in range(size):
                    seg = horiz_wall_segment(not layout['horiz_open'][r][c], bool(layout['horiz'][r][c]), 'D')
                    for ch in seg:
                        attr = curses.color_pair(1) if ch in "─D" else 0
                        stdscr.addch(y, x, ch, attr)
                        x += 1
                    if c < size - 1:
                        stdscr.addch(y, x, "┼", curses.color_pair(1))
                        x += 1
                stdscr.addch(y, x, "┤", curses.color_pair(1))
                y += 1

        bottom = "└" + (("─" * cell_w) + "┴") * (size - 1) + ("─" * cell_w) + "┘"
        for i, ch in enumerate(bottom):
            stdscr.addch(y, i, ch, curses.color_pair(1))
        y += 1

        # key
        key_lines = [
            "E: Dead End (boss start)",
            "S: Sealed Entrance (player start)",
            "X: Exit",
            "Numbers: Enemies/Treasures",
            "D: Door  L: Loop Marker",
            "Yellow center: Players",
            "Red enemy #: Boss",
            "Blue center: Visited w/ enemies",
            "Tab: Switch  Arrows: Move",
            "T: -Treasure  E: -Enemy  Q: Quit"
        ]
        key_x = size * (cell_w + 1) + 3
        key_y = 1
        for i, line in enumerate(key_lines):
            if key_y + i < height:
                stdscr.addstr(key_y + i, key_x, line)

        stdscr.refresh()

    stdscr.timeout(500)
    while True:
        draw_map()
        key = stdscr.getch()
        if key == -1:
            blink_state = not blink_state
            continue
        elif key == ord('q') or key == ord('Q'):
            break
        elif key == 9:  # tab
            selected = 'boss' if selected == 'player' else 'player'
        elif key in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
            current_pos = player_pos if selected == 'player' else boss_pos
            r, c = _rc(current_pos, size)
            direction_map = {curses.KEY_UP: 'up', curses.KEY_DOWN: 'down', curses.KEY_LEFT: 'left', curses.KEY_RIGHT: 'right'}
            direction = direction_map.get(key)
            
            # Check for loop door first
            if loop_pos[r][c] == direction and current_pos in loop_marker_to_target:
                target = loop_marker_to_target[current_pos]
            else:
                # Try normal movement
                if key == curses.KEY_UP:
                    nr, nc = r - 1, c
                elif key == curses.KEY_DOWN:
                    nr, nc = r + 1, c
                elif key == curses.KEY_LEFT:
                    nr, nc = r, c - 1
                elif key == curses.KEY_RIGHT:
                    nr, nc = r, c + 1
                
                if 0 <= nr < size and 0 <= nc < size:
                    next_idx = _idx(nr, nc, size)
                    edge = tuple(sorted([current_pos, next_idx]))
                    if edge in edges:
                        target = next_idx
                    else:
                        target = None
                else:
                    target = None
            
            if target is not None:
                if selected == 'player':
                    enemies = room_info[player_pos][0]
                    if enemies > 0:
                        blue_highlights.add(player_pos)
                    else:
                        blue_highlights.discard(player_pos)
                    player_pos = target
                else:
                    boss_pos = target
                    if target in blue_highlights:
                        blue_highlights.remove(target)
        elif key in (ord('t'), ord('T')):
            current_pos = player_pos if selected == 'player' else boss_pos
            e, t, f = room_info[current_pos]
            room_info[current_pos] = (e, max(0, t - 1), f)
        elif key in (ord('e'), ord('E')):
            current_pos = player_pos if selected == 'player' else boss_pos
            e, t, f = room_info[current_pos]
            room_info[current_pos] = (max(0, e - 1), t, f)

if __name__ == "__main__":
    layout = generate_room_map(LABYRINTH_SIZE)
    curses.wrapper(interactive_map, layout, LABYRINTH_SIZE)


