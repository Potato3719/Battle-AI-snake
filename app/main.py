import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

# heroku testing

@bottle.route('/')
def index():
    return '''
	Battlesnake documentation can be found at
	<a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
	'''


@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')


@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()


@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print("start part")
    print("================\n")
    # print(json.dumps(data))

    color = "#0037ff"
    headType = "silly"
    tailType = "freckled"

    return start_response(color, headType, tailType)


def init(data):
    print("init")
    print("=================\n")
    datastring = json.dumps(data)
    datastore = json.loads(datastring)
    # print(datastore)
    print("Turn: " + str(datastore['turn']))
    myhead = list(datastore['you']['body'][0].values())
    mybody = []
    mylength = len(datastore['you']['body'])

    for coords in datastore['you']['body']:
        mybody.append(list(coords.values()))
    print("myhead\n" + "===========\n" + str(myhead) + "\n")
    print("mybody\n" + "===========\n" + str(mybody) + "\n")

    snakexy = []
    snakehead = []
    snakeid = []
    snakelength = []

    for snake in datastore['board']['snakes']:
        # onesnakexy = [] #one snake's body
        snakeid.append(snake['id'])

        snakelength.append(len(snake['body']));

        snakehead.append(list(snake['body'][
                                  0].values()))  # append all snakes head coordinates to an array of snake heads (eachcoordsofhead array in allsnakearray) (2dArray)
        for coords in snake['body']:
            if list(coords.values()) not in snakexy:
                snakexy.append(list(coords.values()))

    # if snake['health'] == 90: # if snake just ate, do not delete tail
    # for coords in snake['body']:
    # if list(coords.values()) not in snakexy:
    # snakexy.append(list(coords.values())) #append each coords of snake's body to that particular snake

    # else:
    # for coords in snake['body'][:-1]: # if snake didnt eat, delete tail because on next move it will be safe.
    # if list(coords.values()) not in snakexy:
    # snakexy.append(list(coords.values())) #append each coords of snake's body to that particular snake

    print("snakeid\n" + "===========\n" + str(snakeid) + "\n")
    print("snakelength\n" + "===========\n" + str(snakelength) + "\n")
    print("snakexy\n" + "===========\n" + str(snakexy) + "\n")
    print("snakehead")
    print("=========")
    print(snakehead)

    height = datastore["board"]["height"]
    width = datastore["board"]["width"]

    wall = []  # 2d array of coordinates

    for i in range(0, height):
        wall.append([-1, i])

    for i in range(0, height):
        wall.append([width - 1, i])

    for i in range(1, width - 1):
        wall.append([i, 0])

    for i in range(1, width - 1):
        wall.append([i, height - 1])

    food_x = []
    food_y = []

    for i in range(0, len(datastore["board"]["food"])):
        food_x.append(int(datastore["board"]["food"][i]["x"]))
        food_y.append(int(datastore["board"]["food"][i]["y"]))

    # to get my position
    my_position_x = []
    my_position_y = []

    for i in range(0, len(datastore["you"]["body"])):
        my_position_x.append(int(datastore["you"]["body"][i]["x"]))
        my_position_y.append(int(datastore["you"]["body"][i]["y"]))

    return wall, myhead, mybody, mylength, snakehead, snakexy, snakeid, snakelength, height, width, food_x, food_y, my_position_x, my_position_y


# snakexy now does not include tails that disappear in the next iteration

@bottle.post('/move')
def move():
    data = bottle.request.json
    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print("move part")
    print("================\n")
    wall, myhead, mybody, mylength, snakehead, snakexy, snakeid, snakelength, height, width, food_x, food_y, my_position_x, my_position_y = init(
        data)

    safe = []

    # avoid all obstacles
    right = [myhead[0] + 1, myhead[1]]
    left = [myhead[0] - 1, myhead[1]]
    down = [myhead[0], myhead[1] + 1]
    up = [myhead[0], myhead[1] - 1]

    snakexyexcepttailplusheadposiblemoves = snakexy
    # print("snakexyexcepttailplusheadposiblemoves\n" + "===========\n" + str(snakexyexcepttailplusheadposiblemoves) + "\n")
    snakeheadexceptmine = snakehead
    snakeheadexceptmine.remove(myhead)
    # print("snakeheadexceptmine\n" + "===========\n" + str(snakeheadexceptmine) + "\n")

    killpotential = []
    j = 0
    for onesnakehead in snakehead:
        headright = [onesnakehead[0] + 1, onesnakehead[1]]
        headleft = [onesnakehead[0] - 1, onesnakehead[1]]
        headdown = [onesnakehead[0], onesnakehead[1] + 1]
        headup = [onesnakehead[0], onesnakehead[1] - 1]
        if onesnakehead == myhead:  # if head is my own
            j += 1
        elif snakelength[j] < mylength:  # if mylength is longer, dont add it as a threat, add it as a kill potential
            killpotential.append(headright)
            killpotential.append(headleft)
            killpotential.append(headdown)
            killpotential.append(headup)
            j += 1
        else:
            if headright not in snakexyexcepttailplusheadposiblemoves:
                snakexyexcepttailplusheadposiblemoves.append(headright)
            if headleft not in snakexyexcepttailplusheadposiblemoves:
                snakexyexcepttailplusheadposiblemoves.append(headleft)
            if headup not in snakexyexcepttailplusheadposiblemoves:
                snakexyexcepttailplusheadposiblemoves.append(headup)
            if headdown not in snakexyexcepttailplusheadposiblemoves:
                snakexyexcepttailplusheadposiblemoves.append(headdown)

    print(
        "snakexyexcepttailplusheadposiblemoves\n" + "===========\n" + str(snakexyexcepttailplusheadposiblemoves) + "\n")

    safezone = []

    if right not in snakexyexcepttailplusheadposiblemoves and right[0] != height:  # right direction
        # right is safe
        safezone.append(right)
        safe.append("right")
    if left not in snakexyexcepttailplusheadposiblemoves and left[0] != -1:
        safezone.append(left)
        safe.append("left")
    if down not in snakexyexcepttailplusheadposiblemoves and down[1] != height:
        safezone.append(down)
        safe.append("down")
    if up not in snakexyexcepttailplusheadposiblemoves and up[1] != -1:
        safezone.append(up)
        safe.append("up")

    safeandkillpotential = []

    safeandkillpotential = [value for value in killpotential if value in safezone]

    dir = []
    if safeandkillpotential:  # if there is a safe and kill potential zone, append direction to zone that kills and is safe
        if right in safeandkillpotential:
            dir.append("right")
        if left in safeandkillpotential:
            dir.append("left")
        if down in safeandkillpotential:
            dir.append("down")
        if up in safeandkillpotential:
            dir.append("up")

        dirsafekill = random.choice(dir)

    else:
        dirsafekill = random.choice(safe)  # if no safe and kill potential zone, append direction to only safe

    # print("moveresponse\n" + "==========\n" + str(direction) + "\n")
    # return move_response(dirsafekill)

    # DEADEND

    safer = []
    mybody_x = []
    mybody_y = []

    for i in range(0, len(mybody)):
        mybody_x.append(mybody[i][0])

    for j in range(0, len(mybody)):
        mybody_y.append(mybody[j][1])

    # check the lower risk dead end direction
    if len(safe) == 3:
        # 1st case 3 ways to go
        # direction is down which have ["down", "right", "left"] choice
        if "up" not in safe:
            # check right and left (x do not contain any body part)
            if right[0] in mybody_x and left[0] not in mybody_x:
                safer.append("left")
                safer.append("down")
            # direction = random.choice(safer)
            elif left[0] in mybody_x and right[0] not in mybody_x:
                safer.append("right")
                safer.append("down")
            # direction = random.choice(safer)
            elif left[0] in mybody_x and right[0] in mybody_x:
                wall_body_zero = []
                wall_body_width = []
                body_head_y = mybody_y[0]
                for num, i in enumerate(mybody_x):
                    if mybody_x[num] == min(mybody_x):
                        wall_body_zero.append(mybody_y[num])
                    if mybody_x[num] == max(mybody_x):
                        wall_body_width.append(mybody_y[num])

                if max(wall_body_zero) > max(wall_body_width):
                    safer.append("down")
                    if body_head_y > max(wall_body_zero):
                        safer.append("right")
                    else:
                        safer.append("left")
                else:
                    safer.append("down")
                    if body_head_y > max(wall_body_width):
                        safer.append("left")
                    else:
                        safer.append("right")
            # direction = random.choice(safer)
            else:
                # direction = random.choice(safe)
                safer = safe
        # direction is up which have ["up", "right", "left"] choice
        elif "down" not in safe:
            # check right and left (x do not contain any body part)
            if right[0] in mybody_x and left[0] not in mybody_x:
                safer.append("left")
                safer.append("up")
            # direction = random.choice(safer)
            elif left[0] in mybody_x and right[0] not in mybody_x:
                safer.append("right")
                safer.append("up")
            # direction = random.choice(safer)
            elif left[0] in mybody_x and right[0] in mybody_x:
                wall_body_zero = []
                wall_body_width = []
                body_head_y = mybody_y[0]
                for num, i in enumerate(mybody_x):
                    if mybody_x[num] == min(mybody_x):
                        wall_body_zero.append(mybody_y[num])
                    if mybody_x[num] == max(mybody_x):
                        wall_body_width.append(mybody_y[num])

                if max(wall_body_zero) < max(wall_body_width):
                    safer.append("up")
                    if body_head_y > max(wall_body_zero):
                        safer.append("left")
                    else:
                        safer.append("right")
                else:
                    safer.append("up")
                    if body_head_y > max(wall_body_width):
                        safer.append("left")
                    else:
                        safer.append("right")
            # direction = random.choice(safer)
            else:
                # direction = random.choice(safe)
                safer = safe
        # direction is left which have ["up", "down", "left"] choice
        elif "right" not in safe:
            # check up and down (y do not contain any body part)
            if up[1] in mybody_y and down[1] not in mybody_y:
                safer.append("down")
                safer.append("left")
            # direction = random.choice(safer)
            elif down[1] in mybody_y and up[1] not in mybody_y:
                safer.append("up")
                safer.append("left")
            # direction = random.choice(safer)
            elif down[1] in mybody_y and up[1] in mybody_y:
                wall_body_zero = []
                wall_body_height = []
                body_head_x = mybody_x[0]
                for num, i in enumerate(mybody_y):
                    if mybody_y[num] == min(mybody_y):
                        wall_body_zero.append(mybody_x[num])
                    if mybody_y[num] == max(mybody_y):
                        wall_body_height.append(mybody_x[num])

                if max(wall_body_zero) < max(wall_body_height):
                    safer.append("left")
                    if body_head_x < min(wall_body_zero):
                        safer.append("down")
                    else:
                        safer.append("up")
                else:
                    safer.append("left")
                    if body_head_x < min(wall_body_height):
                        safer.append("up")
                    else:
                        safer.append("down")
            # direction = random.choice(safer)
            else:
                # direction = random.choice(safe)
                safer = safe
        # direction is right which have ["up", "down", "right"] choice
        else:
            if up[1] in mybody_y and down[1] not in mybody_y:
                safer.append("down")
                safer.append("right")
            # direction = random.choice(safer)
            elif down[1] in mybody_y and up[1] not in mybody_y:
                safer.append("up")
                safer.append("right")
            # direction = random.choice(safer)
            elif down[1] in mybody_y and up[1] in mybody_y:
                wall_body_zero = []
                wall_body_height = []
                body_head_x = mybody_x[0]
                for num, i in enumerate(mybody_y):
                    if mybody_y[num] == min(mybody_y):
                        wall_body_zero.append(mybody_x[num])
                    if mybody_y[num] == max(mybody_y):
                        wall_body_height.append(mybody_x[num])

                if max(wall_body_zero) > max(wall_body_height):
                    safer.append("right")
                    if body_head_x > max(wall_body_zero):
                        safer.append("down")
                    else:
                        safer.append("up")
                else:
                    safer.append("right")
                    if body_head_x > max(wall_body_height):
                        safer.append("up")
                    else:
                        safer.append("down")

            # direction = random.choice(safer)
            else:
                # direction = random.choice(safe)
                safer = safe
    elif len(safe) == 2:
        # 2nd case 2 ways to go when there is a wall or other snakes
        # only consider ["up", "down"] or ["right", "left"] (when go into the wall)
        # ["up", "down"] case
        if "right" not in safe and "left" not in safe:
            if up[1] in mybody_y and down[1] not in mybody_y:
                # direction = "down"
                safer.append("down")
            elif down[1] in mybody_y and up[1] not in mybody_y:
                # direction = "up"
                safer.append("up")
            elif up[1] in mybody_y and down[1] in mybody_y:
                if 0 in mybody_y and height - 1 not in mybody_y:
                    # direction = "down"
                    safer.append("down")
                elif height - 1 in mybody_y and 0 not in mybody_y:
                    # direction = "up"
                    safer.append("up")
                else:
                    # Check if both my body are close to the wall,
                    # choose the direction with further body part touching the wall
                    wall_body_zero = []
                    wall_body_height = []
                    body_head_x = mybody_x[0]
                    for num, i in enumerate(mybody_y):
                        if mybody_y[num] == min(mybody_y):
                            wall_body_zero.append(mybody_x[num])
                        if mybody_y[num] == max(mybody_y):
                            wall_body_height.append(mybody_x[num])
                    if max(wall_body_zero) > max(wall_body_height):
                        if body_head_x > max(wall_body_zero):
                            # direction = "down"
                            safer.append("down")
                        else:
                            # direction = "up"
                            safer.append("up")
                    else:
                        if body_head_x > max(wall_body_height):
                            # direction = "up"
                            safer.append("up")
                        else:
                            # direction = "down"
                            safer.append("down")
            else:
                safer = safe
        elif "up" not in safe and "down" not in safe:
            print("check right/left case")
            if right[0] in mybody_x and left[0] not in mybody_x:
                print("check right done")
                # direction = "left"
                safer.append("left")
            elif left[0] in mybody_x and right[0] not in mybody_x:
                print("check left done")
                # direction = "right"
                safer.append("right")
            elif left[0] in mybody_x and right[0] in mybody_x:
                if 0 in mybody_x:
                    # direction = "right"
                    safer.append("right")
                elif width - 1 in mybody_x:
                    # direction = "left"
                    safer.append("left")
                else:
                    # check if both body are close to the wall,
                    # choose the direction with further body part touching the wall
                    wall_body_zero = []
                    wall_body_width = []
                    body_head_y = mybody_y[0]
                    for num, i in enumerate(mybody_x):
                        if mybody_x[num] == min(mybody_x):
                            wall_body_zero.append(mybody_y[num])
                        if mybody_x[num] == max(mybody_x):
                            wall_body_width.append(mybody_y[num])
                    if max(wall_body_zero) > max(wall_body_width):
                        if body_head_y > max(wall_body_width):
                            # direction = "left"
                            safer.append("left")
                        else:
                            # direction = "right"
                            safer.append("right")
                    else:
                        if body_head_y > max(wall_body_width):
                            # direction = "left"
                            safer.append("left")
                        else:
                            # direction = "right"
                            safer.append("right")
            else:
                # direction = random.choice(safe)
                safer = safe
        else:
            # direction = random.choice(safe)
            safer = safe
    else:
        # direction = random.choice(safe)
        safer = safe

    print("safer")
    print(safer)

    # CHECKINGFOODWITHSAFER

    # the 4 direction we can go
    left_x = my_position_x[0] - 1
    right_x = my_position_x[0] + 1
    down_y = my_position_y[0] + 1
    up_y = my_position_y[0] - 1

    # now let's see who is the closest snake to us

    min_dist_dict = {}

    # Check for right
    if "right" in safer:
        distance_min = 9999999999
        for i in range(0, len(food_x)):
            x = food_x[i] - right_x
            y = food_y[i] - my_position_y[0]
            distance = x ** 2 + y ** 2
            if distance_min > distance:
                distance_min = distance
        min_dist_dict["right"] = distance_min

    if "left" in safer:
        distance_min = 9999999999
        for i in range(0, len(food_x)):
            x = food_x[i] - left_x
            y = food_y[i] - my_position_y[0]
            distance = x ** 2 + y ** 2
            if distance_min > distance:
                distance_min = distance
        min_dist_dict["left"] = distance_min

    if "down" in safer:
        distance_min = 9999999999
        for i in range(0, len(food_x)):
            x = food_x[i] - my_position_x[0]
            y = food_y[i] - down_y
            distance = x ** 2 + y ** 2
            if distance_min > distance:
                distance_min = distance
        min_dist_dict["down"] = distance_min

    if "up" in safer:
        distance_min = 9999999999
        for i in range(0, len(food_x)):
            x = food_x[i] - my_position_x[0]
            y = food_y[i] - up_y
            distance = x ** 2 + y ** 2
            if distance_min > distance:
                distance_min = distance
        min_dist_dict["up"] = distance_min

    direction = min(min_dist_dict, key=min_dist_dict.get)

    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print("=========")
    print("end")
    # print(json.dumps(data))

    return end_response()


# Expose WSGI app (so gunicorn can find it)


application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )