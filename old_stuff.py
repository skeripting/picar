"""return '''
        <h1>Awesome Car Controls</h1>
        <h2>Manual Control</h2>
        <form action="/move_forward" method="post">
            Speed: <input name="speed" type="number" min="0" max="100" />
            <input value="Move Forward" type="submit" />
        </form>
        <form action="/move_backward" method="post">
            Speed: <input name="speed" type="number" min="0" max="100" />
            <input value="Move Backward" type="submit" />
        </form>
        <form action="/buzz" method="post">
            <input value="Jingle Bells" type="submit" />
        </form>
    '''"""

    
"""def do_move_forward():
    speed = request.forms.get('speed')
    move_forward(int(speed))
    time.sleep(5)
    move_forward(0)
    return "<h1>Moved Forward!</h1>""""