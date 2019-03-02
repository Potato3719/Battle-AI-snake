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
    # print("init")
    # print("=================\n")
    datastring = json.dumps(data)
    datastore = json.loads(datastring)
    # print(datastore)
    print("Turn: " + str(datastore['turn']))
    myhead = list(datastore['you']['body'][0].values())
    mybody = []
    mylength = len(datastore['you']['body'])
    myhealth = datastore['you']['health']

    for coords in datastore['you']['body']:
        mybody.append(list(coords.values()))

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

    return wall, myhead, mybody, mylength, myhealth, snakehead, snakexy, snakeid, snakelength, height, width, food_x, food_y, my_position_x, my_position_y


# snakexy now does not include tails that disappear in the next iteration

def dist_calc(target, test1, test2):  # test1 must be zero, test 2 must be body width or height
    # if the minimum is in zero, return True, if the minimum is in width or height, return False
    test1_output = [abs(target - x) for x in test1]
    test2_output = [abs(target - x) for x in test2]
    print("test1_output\n" + "===========\n" + str(test1_output) + "\n")
    print("test2_output\n" + "===========\n" + str(test2_output) + "\n")
    if min(test1_output) < min(test2_output):
        print("dist_calc returns True\n")
        return True;
    else:
        print("dist_calc returns True\n")
        return False;


@bottle.post('/move')
def move():
    data = bottle.request.json
    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    # print("move part================\n")
    wall, myhead, mybody, mylength, myhealth, snakehead, snakexy, snakeid, snakelength, height, width, food_x, food_y, my_position_x, my_position_y = init(
        data)

    safe = []

    # avoid all obstacles
    right = [myhead[0] + 1, myhead[1]]
    left = [myhead[0] - 1, myhead[1]]
    down = [myhead[0], myhead[1] + 1]
    up = [myhead[0], myhead[1] - 1]

    snakexyexcepttailplusheadposiblemoves = snakexy
    snakeheadexceptmine = snakehead
    snakeheadexceptmine.remove(myhead)


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


    safezone = []

    dirkillpotential = []

    if killpotential:  # if there is kill potential zone, append direction to zone that kills
        if right in killpotential:
            dirkillpotential.append("right")
        if left in killpotential:
            dirkillpotential.append("left")
        if down in killpotential:
            dirkillpotential.append("down")
        if up in killpotential:
            dirkillpotential.append("up")

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

    if not safe:
        safe = snakexy  # if there is no safe zone, take risk of longer snake and pray they dont go that block.


    print("safe\n" + "===========\n" + str(safe) + "\n")

    # print("moveresponse\n" + "==========\n" + str(direction) + "\n")
    # return move_response(dirsafekill)

    # DEADEND

    # 1. Check every point starting from one corner and moving to the other, in either rows or columns, it doesn't matter. Once you reach a point that has three or more orthogonally adjacent walls, mark that point as a dead end, and go to 2.
    # 2. Find the direction of the empty space next to this point (if any), and check every point in that direction. For each of those points: if it has two or more adjacent walls, mark it as a dead end. If it has only one wall, go to 3. If it has no walls, stop checking in this direction and continue with number 1.
    # 3. In every direction that does not have a wall, repeat number 2.

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
            if left[0] in mybody_x and right[0] in mybody_x:
                wall_body_zero = []
                wall_body_width = []
                body_head_y = mybody_y[0]
                for num, i in enumerate(mybody_x):
                    if mybody_x[num] == min(mybody_x):
                        wall_body_zero.append(mybody_y[num])
                    if mybody_x[num] == max(mybody_x):
                        wall_body_width.append(mybody_y[num])

                safer.append("down")
                to_go = dist_calc(body_head_y, wall_body_zero, wall_body_width)
                # if the minimum is in zero, to_go is True, if the minimum is in width or height, to_go is False
                if to_go == True:
                    safer.append("right")
                else:
                    safer.append("left")
            else:
                safer = safe
        # direction is up which have ["up", "right", "left"] choice
        elif "down" not in safe:
            # check right and left (x do not contain any body part)
            if left[0] in mybody_x and right[0] in mybody_x:
                wall_body_zero = []
                wall_body_width = []
                body_head_y = mybody_y[0]
                for num, i in enumerate(mybody_x):
                    if mybody_x[num] == min(mybody_x):
                        wall_body_zero.append(mybody_y[num])
                    if mybody_x[num] == max(mybody_x):
                        wall_body_width.append(mybody_y[num])

                safer.append("up")
                to_go = dist_calc(body_head_y, wall_body_zero, wall_body_width)
                # if the minimum is in zero, to_go is True, if the minimum is in width or height, to_go is False
                if to_go == True:
                    safer.append("right")
                else:
                    safer.append("left")
            else:
                safer = safe
        # direction is left which have ["up", "down", "left"] choice
        elif "right" not in safe:
            if down[1] in mybody_y and up[1] in mybody_y:
                wall_body_zero = []
                wall_body_height = []
                body_head_x = mybody_x[0]
                for num, i in enumerate(mybody_y):
                    if mybody_y[num] == min(mybody_y):
                        wall_body_zero.append(mybody_x[num])
                    if mybody_y[num] == max(mybody_y):
                        wall_body_height.append(mybody_x[num])

                safer.append("left")
                to_go = dist_calc(body_head_x, wall_body_zero, wall_body_height)
                # if the minimum is in zero, to_go is True, if the minimum is in width or height, to_go is False
                if to_go == True:
                    safer.append("down")
                else:
                    safer.append("up")
            else:
                safer = safe
        # direction is right which have ["up", "down", "right"] choice
        else:
            if up[1] in mybody_y and down[1] not in mybody_y:
                safer.append("down")
                safer.append("right")
            elif down[1] in mybody_y and up[1] not in mybody_y:
                safer.append("up")
                safer.append("right")
            elif down[1] in mybody_y and up[1] in mybody_y:
                wall_body_zero = []
                wall_body_height = []
                body_head_x = mybody_x[0]
                for num, i in enumerate(mybody_y):
                    if mybody_y[num] == min(mybody_y):
                        wall_body_zero.append(mybody_x[num])
                    if mybody_y[num] == max(mybody_y):
                        wall_body_height.append(mybody_x[num])
                safer.append("right")
                to_go = dist_calc(body_head_x, wall_body_zero, wall_body_height)
                # if the minimum is in zero, to_go is True, if the minimum is in width or height, to_go is False
                if to_go == True:
                    safer.append("down")
                else:
                    safer.append("up")

            else:
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
                wall_body_zero = []
                wall_body_height = []
                body_head_x = mybody_x[0]
                for num, i in enumerate(mybody_y):
                    if mybody_y[num] == min(mybody_y):
                        wall_body_zero.append(mybody_x[num])
                    if mybody_y[num] == max(mybody_y):
                        wall_body_height.append(mybody_x[num])
                to_go = dist_calc(body_head_x, wall_body_zero, wall_body_height)
                # if the minimum is in zero, to_go is True, if the minimum is in width or height, to_go is False
                if to_go == True:
                    safer.append("down")
                else:
                    safer.append("up")

            else:
                safer = safe
        elif "up" not in safe and "down" not in safe:
            print("check right/left case")
            if right[0] in mybody_x and left[0] not in mybody_x:
                print("check right done")
                safer.append("left")
            elif left[0] in mybody_x and right[0] not in mybody_x:
                print("check left done")
                safer.append("right")
            elif left[0] in mybody_x and right[0] in mybody_x:
                # if 0 in mybody_x:
                # # direction = "right"
                # safer.append("right")
                # elif width-1 in mybody_x:
                # # direction = "left"
                # safer.append("left")
                # else:
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
                to_go = dist_calc(body_head_y, wall_body_zero, wall_body_width)
                # if the minimum is in zero, to_go is True, if the minimum is in width or height, to_go is False
                if to_go == True:
                    safer.append("right")
                else:
                    safer.append("left")
            else:
                safer = safe
        else:
            safer = safe
    else:
        safer = safe

    # print("safer")
    # print(safer)
    # print("direction")
    # print(direction)
    print("safer\n" + "===========\n" + str(safer) + "\n")
    print("dirkillpotential\n" + "===========\n" + str(dirkillpotential) + "\n")
    dirkillpotentialandsafer = [value for value in dirkillpotential if value in safer]
    print("dirkillpotentialandsafer\n" + "===========\n" + str(dirkillpotentialandsafer) + "\n")
    if myhealth > 50 and dirkillpotentialandsafer:
        direction = random.choice(dirkillpotentialandsafer)
        print("direction\n" + "===========\n" + str(direction) + "\n")
        return move_response(direction)

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

    # dir = 0

    # for i in range(0 , 3):
    # if distance_min[i] == min(distance_min):
    # dir = i

    direction = min(min_dist_dict, key=min_dist_dict.get)
    print("direction\n" + "===========\n" + str(direction) + "\n")
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