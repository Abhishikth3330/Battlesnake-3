import typing_extensions


def get_next(currentHead, nextMove):
    """
    return the coordinate of the head if our snake goes that way
    """
    futureHead = currentHead.copy()
    if nextMove == 'left':
        futureHead['x'] = currentHead['x'] - 1
    if nextMove == 'right':
        futureHead['x'] = currentHead['x'] + 1
    if nextMove == 'up':
        futureHead['y'] = currentHead['y'] + 1
    if nextMove == 'down':
        futureHead['y'] = currentHead['y'] - 1
    return futureHead

def get_all_moves(coord):
    # return a list of all coordinates reachable from this point
    return [{'x' : coord['x'] + 1, 'y':coord['y']}, {'x' : coord['x'] - 1, 'y':coord['y']}, {'x' : coord['x'], 'y':coord['y'] + 1}, {'x' : coord['x'], 'y':coord['y'] - 1}]

def get_safe_moves(possible_moves, body, board):
    safe_moves = []

    for guess in possible_moves:
        guess_coord = get_next(body[0], guess)
        if avoid_walls(guess_coord, board["width"], board["height"]) and avoid_snakes(guess_coord, board["snakes"]):
            safe_moves.append(guess)
        elif len(body) > 1 and guess_coord == body[-1] and guess_coord not in body[:-1]:
            safe_moves.append(guess)
    return safe_moves


def avoid_walls(future_head, board_width, board_height):
    result = True

    x = int(future_head["x"])
    y = int(future_head["y"])

    if x < 0 or y < 0 or x >= board_width or y >= board_height:
        result = False

    return result

def avoid_consumption(future_head, snake_bodies, my_snake):
    if len(snake_bodies) < 2:
        return True

    my_length = my_snake['length']
    for snake in snake_bodies:
        if snake == my_snake:
            continue
        if future_head in get_all_moves(snake['head']) and future_head not in snake['body'][1:-1] and my_length <= snake['length']:
            return False
    return True

def avoid_hazards(future_head, hazards):
    return future_head not in hazards

def avoid_snakes(future_head, snake_bodies):
    for snake in snake_bodies:
        if future_head in snake["body"][:-1]:
            return False
    return True


def get_minimum_moves(start_coord, targets):
    moves = []
    for coord in targets:
        moves.append(abs(coord['x'] - start_coord['x']) + abs(coord['y'] - start_coord['y']))
    return moves

def at_wall(coord, board):
    return coord['x'] <= 0 or coord['y'] <= 0 or coord['x'] >= board['width'] - 1 or coord['y'] >= board['height'] - 1

def get_future_head_positions(body, turns, board):
    turn = 0
    explores = {}
    explores[0] = [body[0]]
    while turn < turns:
        turn += 1
        explores[turn] = []
        for explore in explores[turn-1]:
            next_path = get_safe_moves(['left', 'right', 'up', 'down'], [explore], board)
            for path in next_path:
                explores[turn].append(get_next(explore, path))

    return explores[turns]

def retrace_path(path, origin):
    val = []
    next_moves = [move for move in get_all_moves(origin) if move in path]
    while next_moves:
        step = []
        for coord in next_moves:
            val.append(coord)
            step += [move for move in get_all_moves(coord) if move in path and move not in step and move not in val]
        next_moves = step
    return val

def get_str(coord):
    return f"{coord['x']}:{coord['y']}"

def get_moves_towards(start_coord, end_coord):
    ans = []
    if end_coord['x'] > start_coord['x']:
        ans.append('right')
    if end_coord['x'] < start_coord['x']:
        ans.append('left')
    if end_coord['y'] > start_coord['y']:
        ans.append('up')
    if end_coord['y'] < start_coord['y']:
        ans.append('down')
    return ans


def get_excluded_path(path, moves, origin):
    # return cells that are blocked if a snake moves in any specified direction
    #check how many moves from origin are retracing the path
    ans = []
    for coord in path:
        #is this coordinate not blocked by any of the moves ?
        if 'up' in moves and coord['y'] < origin['y']:
            ans.append(coord)
        if 'down' in moves and coord['y'] > origin['y'] and coord not in ans:
            ans.append(coord)
        if 'right' in moves and coord['x'] < origin['x'] and coord not in ans:
            ans.append(coord)
        if 'left' in moves and coord['x'] > origin['x'] and coord not in ans:
            ans.append(coord)
    return ans



def get_smart_moves(possible_moves, body, board, my_snake):
    smart_moves = []
    all_moves = ['up' 'down', 'left', 'right']
    avoid_moves = []
    enemy_snakes = [snake for snake in board['snakes'] if snake['id'] != my_snake['id']]

    safe_moves = get_safe_moves(possible_moves, body, board)

    safe_coords = {}
    next_coords = {}
    eating_snakes = []
    collision_threats = []
    collision_targets = {}
    food_step = {}
    dead_ends = {}

    for guess in safe_moves:
        safe_coords[guess] = []
        guess_coord = get_next(body[0], guess)
        next_coords[guess] = guess_coord
        explore_edge = [guess_coord]
        all_coords = [guess_coord]
        next_explore = []

        explore_step = 1
        food_step[guess] = {}

        for _ in body[:-1]:
            next_explore.clear()
            explore_step += 1

            if len(explore_edge) == 0 and guess not in dead_ends:
                dead_ends[guess] = explore_step
            for explore in explore_edge:
                if explore in board['food']:
                    food_step[guess][get_str(explore)] = explore_step - 1
                safe = get_safe_moves(all_moves, [explore], board)
                for safe_move in safe:
                    guess_coord_next = get_next(explore, safe_move)
                    if guess_coord_next not in all_coords:
                        next_explore.append(guess_coord_next)
                # for other snakes
                snake_collide = [coord for coord in get_all_moves(explore) if not avoid_snakes(coord, enemy_snakes)]
                if snake_collide:
                    for coord in snake_collide:
                        for snake in enemy_snakes:
                            if coord in snake['body']:
                                if coord == snake['head']:
                                    # bumping heads with a snake
                                    if snake['length'] >= my_snake['length']:
                                        collision_threats.append(snake['id'])
                                    elif snake['id'] not in collision_targets:
                                        collision_targets[snake['id']] = explore_step
                                    elif collision_targets[snake['id']] > explore_step:
                                        collision_targets[snake['id']] = explore_step

                all_coords += next_explore.copy()
                all_coords.append(explore)
            explore_edge = next_explore.copy()

        safe_coords[guess] += list(map(dict, frozenset(frozenset(coord.items() for coord in all_coords))))

    for path in safe_coords.keys():
        guess_coord = get_next(body[0], path)
        if((len(safe_coords[path]) >= len(body) or
            any(snake['body'][-1] in safe_coords[path] for snake in
                [snake for snake in board['snaked'] if snake['id']])) and
        avoid_consumption(guess, board['snakes'], my_snake) and
        avoid_hazards(guess_coord, board['hazards'])):
            smart_moves.append(path)

    
    # check if snakes are being forced to move in a square that we want
    for snake in enemy_snakes:
        enemy_options = get_safe_moves(all_moves, snake['body'], board)
        if len(enemy_snakes) == 1:
            enemy_must = get_next(snake['body'][0], enemy_options[0])
            if snake['length'] < my_snake['length'] and enemy_must in next_coords.values():
                for move, coord in next_coords.items():
                    if coord == enemy_must:
                        eating_snakes.append(move)
        elif len(enemy_snakes) == 2:
            #snake has two exits
            for enemy_move in enemy_options:
                enemy_may = get_next(snake['head'], enemy_move)
                if snake['length'] < my_snake['length'] and enemy_may in next_coords.values():
                    for move, coord in next_coords.items():
                        available_space = retrace_path(
                            get_excluded_path(safe_coords[move], get_moves_towards(my_snake['head'], snake['head']), my_snake['head']),
                            snake['head'], board['snakes'])
                        if move in smart_moves and coord == enemy_may and len(
                            get_safe_moves(all_moves, [coord], board)) > 0 and not at_wall(coord, board) and len(available_space) >= my_snake['length']:
                            #trying to eat the snake by going towards the move
                            eating_snakes.append(move)

        if not smart_moves and my_snake['head'] not in board['hazard']:
            # try to chase the tail
            tail_neighbors = []
            tail_safe = get_safe_moves(all_moves, [body[-1]], board)
            for tail_safe_direction in tail_safe:
                tail_neighbors.append(get_next(body[-1], tail_safe_direction))

            for path in safe_coords.keys():
                if any(coord in safe_coords(path for coord in tail_neighbors) or body[-1] in safe_coords[path]):
                    #chasing the tail
                    smart_moves.append(move)

            if not smart_moves:
                #tail might be beside my head
                for move in all_moves:
                    test_move = get_next(body[0], move)
                    if test_move == body[-1] and test_move not in body[:-1]:
                        smart_moves.append(move)

            if not smart_moves:
                #maybe its and enemy tail
                for move in safe_coords.keys():
                    test_move = get_next(body[0], move)
                    for snake in enemy_snakes:
                        if test_move == snake['body'][-1] and test_move not in body[:-1] and not any(
                            coord in board['food'] for coord in get_all_moves(snake['body'][0])):
                            smart_moves.append((move))

    #no clear path, try to fit ourself in the longest one
    if safe_coords and not smart_moves and my_snake['head'] not in board['hazards']:
        if enemy_snakes:
            #consider the enemies here
            escape_plan = {}
            for snake in enemy_snakes:
                if abs(my_snake['head']['x'] - snake['head']['x']) <= 2 and abs(my_snake['head']['y'] - snake['head']['y']) <= 2:
                    # we're right next to an enemy
                    for move in safe_coords.keys():
                        escape_plan[move] = len(get_safe_moves(all_moves, [get_next(my_snake['head'], move)], board))
            if escape_plan:
                #try to get away from the enemy
                for move in escape_plan:
                    if escape_plan[move] == max(escape_plan.values()) and move not in smart_moves:
                        #going towards the move there are wscape_plan[move] options
                        smart_moves.append(move)

        if not smart_moves:
            max_squeez = max(map(len, safe_coords.values()))
            squeez_moves = [move for move in safe_coords.keys() if len(safe_coords[move]) == max_squeez]
            max_deadend = -1
            if len(squeez_moves) > 1:
                max_deadend = max(dead_ends.values())
                squeez_moves = [move for move in dead_ends.keys() if dead_ends[move] == max_deadend and move in squeez_moves]
            for squeez_move in squeez_moves:
                if len(safe_coords[squeez_moves] > 2 and avoid_consumption(get_next(body[0], squeez_move), board['snakes'], my_snake)):
                    #squeezing into squeez_move, max_squeez cells in max_deadend steps
                    smart_moves.append(squeez_move)




    # look for food targets
    food_target = []
    if board['food']:
        food_target = [food for food in board['food'] if food not in board['hazards']]

    # if there are snakes larger than us or if our health is low , then look for food
    if (len(smart_moves) > 1 or my_snake['head'] in board['hazards']) and board['food'] and not eating_snakes and (
        my_snake['health'] < hunger_threshold or any (
            snake['length'] + (len(food_target) / 2) >= my_snake['length'] for snake in enemy_snakes)):
            print('snake is hungry')
            food_choice = smart_moves
            food_moves = {}
            closest_food = []
            greed_moves = []
            # food_target contains food
            if not food_target or my_snake['head'] in body['hazards']:
                food_target = board['food']
                #no food outside hazards, now we are considering food_target
            if my_snake['health'] < hunger_threshold or my_snake['length'] < board['width']:
                food_choice = safe_coords.keys()

            for path in food_choice:
                if any(food in safe_coords[path] for food in food_target):
                    food_moves[path] = get_minimum_moves(get_next(body[0], path), [food for food in food_target if food in safe_coords[path]])
                    if food_step[path]:
                        # target_keys = [hash_coord(food) for food in food_target if food in safe_coord[path]]
                        target_keys = [key for key in target_keys if key in food_step[path].keys()]
                        target_steps = [food_step[path][key] for key in target_keys]
                        if target_steps:
                            food_moves[path] = min(target_steps)
            if food_moves:
                closest_food_distance = min(food_moves.values())
                food_considerations = enemy_snakes
            
                if mysnake['head'] in board['hazards'] and closest_food_distance > 2:
                    food_considerations = []

                for path in food_moves.keys():
                    if food_moves[path] <= closest_food_distance:
                        # food that is safe towards this path is closest_food_distance steps away
                        closest_food.append(path)
                        #check if we are closest to the food
                        minimum_moves_threshold = 6
                        for food in food_target:
                            #thinking about eating food
                            test_coord = get_next(my_snake['head'], path)
                            distance_to_me = get_minimum_moves(food, [test_coord])
                            if food_step[path] and hash_coord(food) in food_step[path].keys():
                                distance_to_me = food_step[path][hash_coord(food)]
                            if distance_to_me == food_moves[path]:
                                for snake in food_consumptions:
                                    #considering snake at distance_to_me
                                    if food in get_all_moves(snake['head']) and distance_to_me > 1 and snake['length'] + 1 >= my_snake['length']:
                                        # this food is near enemy snake
                                        avoid_moves.append(path)
                                    elif get_minimum_moves(food,
                                    [snake['head']]) <= distance_to_me + 1 and get_minimum_moves(
                                        snake['head'], [test_coord]) <= minimum_moves_threshold and snake['length'] > my_snake['length']:
                                        #here the other snake is getting to the food so avoid this path
                                        avoid_moves.append(path)
                            if not (path in avoid_moves) and (path in smart_moves):
                                greed_moves.append(path)
                    else:
                        for path in food_choice:
                            food_moves[path] = get_minimum_moves(get_next(body[0], path), food_target)
                        
                        if food_moves:
                            closest_food_distance = min(food_moves.values())
                            for path in food_moves.keys():
                                if closest_food_distance >= food_moves[path] >= my_snake['length'] and not collision_threats:
                                    # distant food target towards path is close_food_distance
                                    closest_food.append(path)
                    if closest_food:
                        if my_snake['health'] < hunger_threshold or greed_moves:
                            #we are either very hungry or greedy
                            hazard_avoid = [move for move in closest_food if get_next(body[0], move) in board['hazards']]
                            if hazard_avoid:
                                if greed_moves:
                                    #choosing greed
                                    smart_moves = greed_moves
                                else:
                                    #staying safe
                                    smart_moves = hazard_avoid
                            else:
                                smart_moves = closest_moves
                        else:
                            food_intersect = [move for move in smart_moves if move in closest_food and move not in avoid_moves]
                            # smart moves and food_moves
                            if food_intersect:
                                smart_moves = food_intersect
                            elif avoid_moves:
                                avoid_test = [move for move in smart_moves if move not in avoid_moves]
                                if avoid_test:
                                    smart_moves = avoid_test
                                        

    #after everything, chase the tail normally, move to center
    if len(smart_moves) > 1:
        from_coord = my_snake['head']
        to_coord = my_snake['body'][-1]
        center_coord = {'x': (board['width'] - 1)/2, 'y':(board['height'] - 1)/2}

        if len(enemy_snakes) == 1:
            enemy = enemy_snakes[0]
            if len(enemy['body']) > len(my_snake['body']):
                to_coord = center_coord
            else:
                to_coord = enemy['head']
        idle_target = get_moves_towards(from_coord, to_coord)
        test_moves = [move for move in smart_moves if move in idle_target]
        if test_moves:
            smart_moves = test_moves

        

    return smart_moves