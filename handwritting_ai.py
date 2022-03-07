import os

from flask import Flask, request
from PIL import Image, ImageDraw



TEMPLATE = \
"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Handwritting Recognition</title>
        <style>
            html, body {
            height: 100%;
            overflow-y: hidden; 
            overflow-x: hidden;
            }
            .canvas {
            margin: 0;
            display: flex;
            /* This centers our sketch horizontally. */
            justify-content: center;
            /* This centers our sketch vertically. */
            align-items: center;
            }
        </style>
        <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
        <script src="https://cdn.jsdelivr.net/npm/p5@1.4.1/lib/p5.js"></script>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
        <script src="//code.jquery.com/jquery-1.12.4.min.js" integrity="sha256-ZosEbRLbNQzLpnKIkEdrPv7lOy9C27hHQ+Xp8a4MxAQ=" crossorigin="anonymous"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/2.2.0/socket.io.js" integrity="sha256-yr4fRk/GU1ehYJPAs8P4JlTgu0Hdsp4ZKrx8bDEDC3I=" crossorigin="anonymous"></script>
        <script>
            
            var Points = [];
            var WIDTH = screen.width;
            var HEIGHT =  screen.height;

            function setup() {
                createCanvas(WIDTH, HEIGHT);
                background(255/2);
                noStroke();
                fill(0);
            }

            function draw() {
                stroke(0);
                coordinate = [mouseX, mouseY, pmouseX, pmouseY];
                if (mouseIsPressed === true) {
                    Points.push(coordinate)
                    line.apply(null, coordinate);
                }
            }

            function giveMeText() {
                var xhr = new XMLHttpRequest();
                xhr.open("POST", '/getHandwritting', true);

                //Send the proper header information along with the request
                xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                xhr.send(JSON.stringify({points : Points, dimension : [WIDTH, HEIGHT]}));
                Points = [];
            }
        </script>

    </head>

    <body class="w3-container">
        <div class="canvas w3-center" id="canvas"></div>
        <div class="w3-display-top w3-margin">
            <p class="w3-small w3-center w3-text-gray">Handwriting AI by L4M5</p>
            <button class="w3-button w3-gray w3-round" onclick="giveMeText()">Give me text</button>
            <button class="w3-button w3-gray w3-round w3-right">Delete</button>
            <input id="theText" type="text">
        </div>

    </body>

    </html>
"""


app = Flask(__name__)

@app.route("/")
def home():

    return TEMPLATE


@app.route('/getHandwritting', methods=['POST'])
def getPoints():
    os.remove('pointsXY.txt')
    f = open('pointsXY.txt', 'a')

    if request.method == 'POST':
        last = None

        for point in request.json.get('points'):
            if point != last:
                last = point
                f.write(",".join(map(str, point)) + '\n')

        f.close()
        createImage(*request.json.get('dimension'))

    return TEMPLATE


def createImage(width, height):
    img = Image.new("RGB", (width, height), (255, 255, 255))
    img.save("image.png", "PNG")

    with Image.open("image.png") as im:

        draw = ImageDraw.Draw(im)
        for i in open('pointsXY.txt').readlines():
            x1,y1,x2,y2 = map(float, i.split(","))
            draw.line(((x1, y1), (x2, y2)), fill=225//2, width=2)
        # draw.line((10, im.size[1], im.size[0], 0), fill=128)

        im.save("image.png", "PNG")




if __name__ == "__main__":
    app.run(debug=True, port=6969)