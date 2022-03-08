import os

from flask import Flask, request, jsonify
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
            
            var xhr = new XMLHttpRequest();
            
            var Points = [];
            var WIDTH = screen.width;
            var HEIGHT =  screen.height;
            var boundingBox = [];
            var showBoundingBox = false;
            var res;

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

                if (showBoundingBox === true){
                    for (let point_xy in Points){
                        line.apply(null, Points[point_xy]);
                    }
                    fill(120);
                    setLineDash([5, 5]); //create the dashed line pattern here
                    rect.apply(null, boundingBox);
                    setLineDash([0, 0]); //create the dashed line pattern here

                }
            }


            function setLineDash(list) {
                drawingContext.setLineDash(list);
            }

            function giveMeText() {
                xhr.open("POST", '/getHandwritting', true);

                //Send the proper header information along with the request
                xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                xhr.send(JSON.stringify({points : Points, dimension : [WIDTH, HEIGHT]}));
                res = JSON.parse(xhr.responseText);
                console.log(res)
                showBoundingBox = true;
                redraw(1);
                showBoundingBox = false;
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



class BoundingBox:
    """ To handle cropping """

    def __init__(self, file):
        self.points = map(
                        lambda x: map(float, x.split(',')), 
                        open(file, 'r').readlines()
                    )
        self.minX = float("inf")
        self.minY = float("inf")
        self.maxX = -float("inf")
        self.maxY = -float("inf")


    def getBoundingBox(self):
        for point in self.points:
            x1,y1,x2,y2 = point
            self.minX = min([self.minX, x1, x2])
            self.minY = min([self.minY, y1, y2])
            self.maxX = max([self.maxX, x1, x2])
            self.maxY = max([self.maxY, y1, y2])

        return {'topLeft': (self.minX, self.maxY),
                'topRight': (self.maxX, self.maxY),
                'bottomRight': (self.maxX, self.minY),
                'bottomLeft': (self.minX, self.minY)
            }


app = Flask(__name__)

@app.route("/")
def home():
    return TEMPLATE


@app.route('/getHandwritting', methods=['POST'])
def getPoints():
    os.remove('pointsXY.txt')
    f = open('pointsXY.txt', 'a')

    last = None

    for point in request.json.get('points'):
        if point != last:
            last = point
            f.write(",".join(map(str, point)) + '\n')

    f.close()
    
    # Create an image of the sketch
    createImage(*request.json.get('dimension'))
    # Get bounding box of the sketch
    return jsonify(BoundingBox('pointsXY.txt').getBoundingBox())


def createImage(width, height):
    img = Image.new("RGB", (width, height), (255, 255, 255))
    img.save("image.png", "PNG")

    with Image.open("image.png") as im:

        draw = ImageDraw.Draw(im)
        for i in open('pointsXY.txt').readlines():
            x1,y1,x2,y2 = map(float, i.split(","))
            draw.line(((x1, y1), (x2, y2)), fill=225//2, width=2)

        im.save("image.png", "PNG")




if __name__ == "__main__":
    app.run(debug=True, port=6969)