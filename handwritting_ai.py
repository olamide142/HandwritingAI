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
        <script src="//code.jquery.com/jquery-1.12.4.min.js" integrity="sha256-ZosEbRLbNQzLpnKIkEdrPv7lOy9C27hHQ+Xp8a4MxAQ="
            crossorigin="anonymous"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/2.2.0/socket.io.js"
            integrity="sha256-yr4fRk/GU1ehYJPAs8P4JlTgu0Hdsp4ZKrx8bDEDC3I=" crossorigin="anonymous"></script>
    </head>

    <body>
        <div class="canvas w3-center" id="canvas"></div>
        <div class="w3-display-top w3-margin">
            <button class="w3-button w3-teal w3-round">Pin Board</button>
            <button class="w3-button w3-teal w3-round">Share</button>
            <button class="w3-button w3-teal w3-round w3-right">Delete</button>
        </div>



        <script>
            var Points = [];

            function setup() {
                createCanvas(screen.width-30, screen.height-70);
                background(0);
                noStroke();
                fill(0);
            }

            function draw() {
                stroke(255);
                if (mouseIsPressed === true) {
                    Points.push([mouseX, mouseY, pmouseX, pmouseY])
                    line(mouseX, mouseY, pmouseX, pmouseY);
                }
            }

            function getDrawings(data) {
                if (data.length == 5 && data[4] == 'draw') {
                    line(data[0], data[1], data[2], data[3]);
                }
            }
        </script>




    </body>

    </html>
"""



from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():

    return TEMPLATE


@app.route('/getHandwritting')
def createImage():
        
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (800, 1280), (255, 255, 255))
    img.save("image.png", "PNG")

    with Image.open("image.png") as im:

        draw = ImageDraw.Draw(im)
        draw.line(((10, 0), (19,19)), fill=128, width=10)
        # draw.line((10, im.size[1], im.size[0], 0), fill=128)

        im.save("image.png", "PNG")




if __name__ == "__main__":
    app.run(debug=True, port=6969)