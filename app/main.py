import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response


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

    myhead = list(datastore['you']['body'][0].values())
    mybody = []

    for coords in datastore['you']['body']:
        mybody.append(list(coords.values()))
    # print("myhead\n" + "===========\n" + str(myhead) + "\n")
    # print("mybody\n" + "===========\n" + str(mybody) + "\n")

    distinctsnakexy = []
    snakexy = []
    snakehead = []

    for snake in datastore['board']['snakes']:
        onesnakexy = []  # one snake's body
        for coords in snake['body']:
            onesnakexy.append(list(coords.values()))  # append each coords of snake's body to that particular snake
            snakexy.append(list(coords.values()))  # append each coords of snake's body to that particular snake
        distinctsnakexy.append(onesnakexy)
        # append all snakes body to an array of snake bodies (eachcoords array in onesnakebody array in allsnake
        # array) (3dArray)
        snakehead.append(list(snake['body'][0].values()))
    # append all snakes head coordinates to an array of snake heads (eachcoordsofhead array in allsnakearray) (2dArray)

    # print("snakexy\n" + "===========\n" + str(snakexy) + "\n")

    # snakexy[0][0] is x, snakexy[0][1] is y ; distinctsnakexy[0] is myself, snakexy[0][0] is my head, snakexy[0][0][0]
    # is my head's x, snakexy[0][0][1] is my head's y

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

    # print("walls\n" + "==========\n" + str(wall) + "\n")

    return wall, myhead, mybody, snakehead, snakexy, height, width


@bottle.post('/move')
def move():
    data = bottle.request.json
    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print("move part")
    print("================")
    wall, myhead, mybody, snakehead, snakexy, height, width = init(data)

    safe = []

    # avoid all obstacles
    right = [myhead[0] + 1, myhead[1]]
    left = [myhead[0] - 1, myhead[1]]
    down = [myhead[0], myhead[1] + 1]
    up = [myhead[0], myhead[1] - 1]

    if right not in snakexy and right[0] != height:  # right direction
        # right is safe
        safe.append("right")
    if left not in snakexy and left[0] != -1:
        safe.append("left")
    if down not in snakexy and down[1] != height:
        safe.append("down")
    if up not in snakexy and up[1] != -1:
        safe.append("up")


    #check dead end
    print("safe")
    print(safe)
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
                direction = random.choice(safer)
            elif left[0] in mybody_x and right[0] not in mybody_x:
                safer.append("right")
                safer.append("down")
                direction = random.choice(safer)
            elif left[0] in mybody_x and right[0] in mybody_x:
                wall_body_zero = []
                wall_body_width = []
                body_head_y = mybody_y[0]
                for i in mybody_x:
                    if mybody_x[i] == 0:
                        wall_body_zero.append(mybody_y[i])
                    if mybody_x[i] == width - 1:
                        wall_body_width.append(mybody_y[i])

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
                direction = random.choice(safer)
            else:
                direction = random.choice(safe)
        # direction is up which have ["up", "right", "left"] choice
        elif "down" not in safe:
            # check right and left (x do not contain any body part)
            if right[0] in mybody_x and left[0] not in mybody_x:
                safer.append("left")
                safer.append("up")
                direction = random.choice(safer)
            elif left[0] in mybody_x and right[0] not in mybody_x:
                safer.append("right")
                safer.append("up")
                direction = random.choice(safer)
            elif left[0] in mybody_x and right[0] in mybody_x:
                wall_body_zero = []
                wall_body_width = []
                body_head_y = mybody_y[0]
                for i in mybody_x:
                    if mybody_x[i] == 0:
                        wall_body_zero.append(mybody_y[i])
                    if mybody_x[i] == width - 1:
                        wall_body_width.append(mybody_y[i])

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
                direction = random.choice(safer)
            else:
                direction = random.choice(safe)
        # direction is left which have ["up", "down", "left"] choice
        elif "right" not in safe:
            # check up and down (y do not contain any body part)
            if up[1] in mybody_y and down[1] not in mybody_y:
                safer.append("down")
                safer.append("left")
                direction = random.choice(safer)
            elif down[1] in mybody_y and up[1] not in mybody_y:
                safer.append("up")
                safer.append("left")
                direction = random.choice(safer)
            elif down[1] in mybody_y and up[1] in mybody_y:
                wall_body_zero = []
                wall_body_height = []
                body_head_x = mybody_x[0]
                for i in mybody_y:
                    if mybody_y[i] == 0:
                        wall_body_zero.append(mybody_x[i])
                    if mybody_y[i] == width:
                        wall_body_height.append(mybody_x[i])

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
                direction = random.choice(safer)
            else:
                direction = random.choice(safe)
        # direction is right which have ["up", "down", "right"] choice
        else:
            if up[1] in mybody_y and down[1] not in mybody_y:
                safer.append("down")
                safer.append("right")
                direction = random.choice(safer)
            elif down[1] in mybody_y and up[1] not in mybody_y:
                safer.append("up")
                safer.append("right")
                direction = random.choice(safer)
            elif down[1] in mybody_y and up[1] in mybody_y:
                wall_body_zero = []
                wall_body_height = []
                body_head_x = mybody_x[0]
                for i in mybody_y:
                    if mybody_y[i] == 0:
                        wall_body_zero.append(mybody_x[i])
                    if mybody_y[i] == width:
                        wall_body_height.append(mybody_x[i])

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

                direction = random.choice(safer)
            else:
                direction = random.choice(safe)
    elif len(safe) == 2:
        # 2nd case 2 ways to go when there is a wall or other snakes
        # only consider ["up", "down"] or ["right", "left"] (when go into the wall)
        # ["up", "down"] case
        if "right" not in safe and "left" not in safe:
            if up[1] in mybody_y and down[1] not in mybody_y:
                direction = "down"
            elif down[1] in mybody_y and up[1] not in mybody_y:
                direction = "up"
            elif up[1] in mybody_y and down[1] in mybody_y:
                if 0 in mybody_y and height-1 not in mybody_y:
                    direction = "down"
                elif height-1 in mybody_y and 0 not in mybody_y:
                    direction = "up"
                else:
                    # Check if both my body are close to the wall,
                    # choose the direction with further body part touching the wall
                    wall_body_zero = []
                    wall_body_height = []
                    body_head_x = mybody_x[0]
                    for i in mybody_y:
                        if mybody_y[i] == 0:
                            wall_body_zero.append(mybody_x[i])
                        if mybody_y[i] == height-1:
                            wall_body_height.append(mybody_x[i])
                    if max(wall_body_zero) > max(wall_body_height):
                        if body_head_x > max(wall_body_zero):
                            direction = "down"
                        else:
                            direction = "up"
                    else:
                        if body_head_x > max(wall_body_height):
                            direction = "up"
                        else:
                            direction = "down"
            else:
                direction = random.choice(safe)
        elif "up" not in safe and "down" not in safe:
            print("check right/left case")
            if right[0] in mybody_x and left[0] not in mybody_x:
                print("check right done")
                direction = "left"
            elif left[0] in mybody_x and right[0] not in mybody_x:
                print("check left done")
                direction = "right"
            elif left[0] in mybody_x and right[0] in mybody_x:
                if 0 in mybody_x:
                    direction = "right"
                elif width-1 in mybody_x:
                    direction = "left"
                else:
                    # check if both body are close to the wall,
                    # choose the direction with further body part touching the wall
                    wall_body_zero = []
                    wall_body_width = []
                    body_head_y = mybody_y[0]
                    for i in mybody_x:
                        if mybody_x[i] == 0:
                            wall_body_zero.append(mybody_y[i])
                        if mybody_x[i] == width:
                            wall_body_width.append(mybody_y[i])
                    if max(wall_body_zero) < max(wall_body_width):
                        if body_head_y > max(wall_body_zero):
                            direction = "left"
                        else:
                            direction = "right"
                    else:
                        if body_head_y > max(wall_body_width):
                            direction = "left"
                        else:
                            direction = "right"
            else:
                direction = random.choice(safe)
        else:
            direction = random.choice(safe)
    else:
        # last case only have one way to go
        direction = random.choice(safe)

    print("safer")
    print(safer)
    print("direction")
    print(direction)
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