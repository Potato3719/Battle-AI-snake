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
    print("================")
    # print(json.dumps(data))

    # color blue
    color = "#003BFF"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json
    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print("move part")
    print("================")
    # print(json.dumps(data))
    json_string = json.dumps(data)
    game_data = json.loads(json_string)
    height = game_data["board"]["height"]
    width = game_data["board"]["width"]

    # to get my postion
    my_position_x = []
    my_position_y = []
    for i in range(0, len(game_data["you"]["body"])):
        my_position_x.append(int(game_data["you"]["body"][i]["x"]))
        my_position_y.append(int(game_data["you"]["body"][i]["y"]))

    print(my_position_x[0])
    print(my_position_y[0])
    print(height)
    print(width)

    # try to not hit wall
    # direction = random.choice(directions)
    directions = ['up', 'down', 'left', 'right']
    if my_position_x[0] == 0:
        if my_position_y[0] == 0:
            if my_position_x[1] == 1:
                direction = 'down'
            else:
                direction = 'right'
        elif my_position_y[0] == height-1:
            if my_position_x[1] == 1:
                direction = 'up'
            else:
                direction = 'right'
        elif my_position_x[1] == 1:
            direction = 'up'
        else:
            direction = 'right'
    elif my_position_x[0] == width-1:
        if my_position_y[0] == 0:
            if my_position_x[1] == width-2:
                direction = 'down'
            else:
                direction = 'left'
        elif my_position_y[0] == height-1:
            if my_position_y[1] == height-2:
                direction = 'left'
            else:
                direction = 'up'
        elif my_position_x[1] == width-2:
            direction = 'up'
        else:
            direction = 'left'
    elif my_position_y[0] == 0 and my_position_x[0] != 0 and my_position_x[0] != width-1:
        if my_position_y[1] == 1:
            direction = 'left'
        else:
            direction = 'down'
    elif my_position_y[0] == height-1 and my_position_x[0] != 0 and my_position_x[0] != width-1:
        if my_position_y[1] == height - 2:
            direction = 'right'
        else:
            direction = 'up'
    else:
        if my_position_x[1] == my_position_x[0] - 1:
            direction = 'right'
        elif my_position_x[1] == my_position_x[0] + 1:
            direction = 'left'
        elif my_position_y[1] == my_position_y - 1:
            direction = 'down'
        else:
            direction = 'up'

    print(direction)
    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print("end part")
    print("================")
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
