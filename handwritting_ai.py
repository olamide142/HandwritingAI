import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image, ImageDraw
import uvicorn
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model


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
            background: #8B4513; /* Brown background */
            margin: 0;
            padding: 0;
            }
            .canvas {
            margin: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            }
            .chalkboard {
            border: 15px solid #654321; /* Dark brown border */
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
            background: #2F4F2F; /* Dark green chalkboard color */
            position: relative;
            }
            .controls {
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            background: rgba(139, 69, 19, 0.95); /* Semi-transparent brown */
            padding: 10px;
            border-radius: 8px;
            z-index: 1000;
            }
            .control-btn {
            background: #8B4513;
            color: white;
            border: 2px solid #654321;
            border-radius: 5px;
            padding: 8px 15px;
            margin: 2px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
            }
            .control-btn:hover {
            background: #A0522D;
            transform: translateY(-2px);
            }
            .control-btn.active {
            background: #CD853F;
            border-color: #DAA520;
            }
            .eraser-btn.active {
            background: #696969;
            border-color: #808080;
            }
            #theText {
            background: white;
            border: 2px solid #654321;
            border-radius: 5px;
            padding: 5px;
            margin: 5px;
            font-size: 16px;
            }
            .brush-controls {
            display: inline-block;
            margin-left: 10px;
            }
            .brush-controls label {
            color: white;
            font-weight: bold;
            }
            .brush-controls span {
            color: white;
            font-weight: bold;
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
            var WIDTH = screen.width * 0.3; // Make canvas smaller to fit border
            var HEIGHT = screen.height * 0.7;
            var boundingBox = [];
            var showBoundingBox = false;
            var res;
            var brushWidth = 20; // Changed pencil width to 20
            var isErasing = false;
            var chalkboardColor = [47, 79, 47]; // Dark green chalkboard color

            function setup() {
                let canvas = createCanvas(WIDTH, HEIGHT);
                canvas.parent('chalkboard');
                background(chalkboardColor[0], chalkboardColor[1], chalkboardColor[2]); // Dark green chalkboard color
                noStroke();
                fill(255); // White chalk
            }

            function updateBrushWidth(val) {
                brushWidth = parseInt(val);
                document.getElementById('brushWidthValue').innerText = val;
            }

            function toggleEraser() {
                isErasing = !isErasing;
                const eraserBtn = document.getElementById('eraserBtn');
                const drawBtn = document.getElementById('drawBtn');
                
                if (isErasing) {
                    eraserBtn.classList.add('active');
                    drawBtn.classList.remove('active');
                } else {
                    eraserBtn.classList.remove('active');
                    drawBtn.classList.add('active');
                }
            }

            function draw() {
                if (isErasing) {
                    // Eraser mode - draw chalkboard green lines
                    stroke(chalkboardColor[0], chalkboardColor[1], chalkboardColor[2]); // Chalkboard green
                    strokeWeight(brushWidth * 2); // Make eraser wider
                } else {
                    // Drawing mode - draw white chalk lines
                    stroke(255, 255, 255); // White chalk
                    strokeWeight(brushWidth);
                }

                coordinate = [mouseX, mouseY, pmouseX, pmouseY];
                if (mouseIsPressed === true) {
                    if (!isErasing) {
                        // Only add points when drawing, not erasing
                        Points.push(coordinate);
                    }
                    line.apply(null, coordinate);
                }

                if (showBoundingBox === true){
                    for (let point_xy in Points){
                        line.apply(null, Points[point_xy]);
                    }
                    fill(120);
                    setLineDash(list); //create the dashed line pattern here
                    rect.apply(null, boundingBox);
                    setLineDash([0, 0]); //create the dashed line pattern here

                }
            }


            function setLineDash(list) {
                drawingContext.setLineDash(list);
            }

            function giveMeText() {
                // Only send points that represent visible drawings (not erased areas)
                var visiblePoints = Points.filter(function(point) {
                    // Filter out any points that might be invalid or represent erased areas
                    return point && point.length === 4 && 
                           !isNaN(point[0]) && !isNaN(point[1]) && 
                           !isNaN(point[2]) && !isNaN(point[3]);
                });
                
                xhr.open("POST", '/getHandwritting', true);
                xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
                xhr.send(JSON.stringify({
                    points: visiblePoints, 
                    dimension: [WIDTH, HEIGHT], 
                    brushWidth: brushWidth
                }));
                
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === 4 && xhr.status === 200) {
                        res = JSON.parse(xhr.responseText);
                        console.log(res);
                        
                        // Display the prediction
                        document.getElementById('theText').value = res.predicted_digit;
                        
                        showBoundingBox = true;
                        redraw(1);
                        showBoundingBox = false;
                    }
                };
            }

            function clearCanvas() {
                Points = [];
                background(chalkboardColor[0], chalkboardColor[1], chalkboardColor[2]); // Reset to chalkboard color
                document.getElementById('theText').value = '';
                // Reset eraser mode
                isErasing = false;
                const eraserBtn = document.getElementById('eraserBtn');
                const drawBtn = document.getElementById('drawBtn');
                eraserBtn.classList.remove('active');
                drawBtn.classList.add('active');
                
                // Reset drawing settings
                stroke(255, 255, 255); // White chalk
                strokeWeight(brushWidth);
                fill(255); // White chalk
            }
        </script>

    </head>

    <body>
        <div class="canvas">
            <div id="chalkboard" class="chalkboard">
                <div class="controls">
                    <p class="w3-small w3-center w3-text-white" style="margin: 0 0 10px 0;">Handwriting AI by Victor Olowofeso</p>
                    <button class="control-btn" onclick="giveMeText()">Recognize</button>
                    <button class="control-btn" onclick="clearCanvas()">Clear All</button>
                    <button class="control-btn active" id="drawBtn" onclick="toggleEraser()">Chalk</button>
                    <button class="control-btn" id="eraserBtn" onclick="toggleEraser()">Eraser</button>
                    <input id="theText" type="text" placeholder="Prediction will appear here">
                    <div class="brush-controls">
                        <label for="brushWidth">Chalk Width:</label>
                        <input type="range" id="brushWidth" min="1" max="20" value="20" oninput="updateBrushWidth(this.value)"> <!-- Changed pencil width to 20 -->
                        <span id="brushWidthValue">20</span> <!-- Changed pencil width to 20 -->
                    </div>
                </div>
            </div>
        </div>
    </body>

    </html>
"""



# Load trained model
MODEL_PATH = "models/simple_mnist.keras"
# MODEL_PATH = "models/emnist.keras"
mnist_model = load_model(MODEL_PATH)

# Initialize FastAPI
app = FastAPI()

# Allow CORS (for browser interaction)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_bounding_box(points):
    """
    Calculate bounding box from drawing points.
    
    Args:
        points: List of [x1, y1, x2, y2] coordinates
        
    Returns:
        Dictionary with bounding box coordinates
    """
    if not points:
        return None
    
    min_x = float('inf')
    min_y = float('inf')
    max_x = -float('inf')
    max_y = -float('inf')
    
    for point in points:
        x1, y1, x2, y2 = point
        min_x = min(min_x, x1, x2)
        min_y = min(min_y, y1, y2)
        max_x = max(max_x, x1, x2)
        max_y = max(max_y, y1, y2)
    
    return {
        'left': int(min_x),
        'top': int(min_y),
        'right': int(max_x),
        'bottom': int(max_y),
        'width': int(max_x - min_x),
        'height': int(max_y - min_y)
    }

def crop_image_with_padding(img, padding=20):
    """
    Crop image to remove excess background and add padding.
    
    Args:
        img: PIL Image
        padding: Extra pixels around the content
        
    Returns:
        Cropped PIL Image
    """
    # Convert to numpy array for easier processing
    img_array = np.array(img)
    
    # Find non-zero (drawn) pixels
    non_zero_coords = np.where(img_array > 0)
    
    if len(non_zero_coords[0]) == 0:
        # No content found, return original image
        return img
    
    # Get the bounds of the content
    min_y, max_y = non_zero_coords[0].min(), non_zero_coords[0].max()
    min_x, max_x = non_zero_coords[1].min(), non_zero_coords[1].max()
    
    # Add padding
    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)
    max_x = min(img.width, max_x + padding)
    max_y = min(img.height, max_y + padding)
    
    # Crop the image
    cropped = img.crop((min_x, min_y, max_x, max_y))
    return cropped

# Pydantic request model
class PointsRequest(BaseModel):
    points: list
    dimension: list
    brushWidth: int = 20  # Changed pencil width to 20

# Drawing handler
def create_image(points, width, height, brush_width=60):
    img = Image.new("L", (width, height), 0)  # Black background (0)
    draw = ImageDraw.Draw(img)
    for x1, y1, x2, y2 in points:
        draw.line(((x1, y1), (x2, y2)), fill=255, width=brush_width)  # White lines (255)
    return img

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(content=TEMPLATE)

@app.post("/getHandwritting")
async def get_handwriting(request: Request):
    data = await request.json()
    points = data.get("points")
    dimension = data.get("dimension")
    brush_width = data.get("brushWidth", 20)

    if not points or not dimension:
        return JSONResponse(status_code=400, content={"error": "Missing data"})

    # Create image
    raw_img = create_image(points, dimension[0], dimension[1], brush_width)
    
    # Crop out excess background with padding
    cropped_img = crop_image_with_padding(raw_img, padding=20)
    
    # Save the cropped image
    cropped_img.save("cropped_image.png", "PNG")
    
    # Resize to 28x28 for model input
    img = cropped_img.resize((28, 28)).convert("L")
    
    # Save the resized image for MNIST format
    img.save("mnist_image.png", "PNG")

    # Normalize and reshape for model
    img_array = np.array(img).astype("float32") / 255.0
    img_array = np.expand_dims(img_array, axis=(0, -1))  # Shape: (1, 28, 28, 1)

    # Predict digit
    prediction = mnist_model.predict(img_array, verbose=0)
    predicted_digit = int(np.argmax(prediction[0]))
    confidence = float(np.max(prediction[0]))

    return JSONResponse({
        "predicted_digit": predicted_digit,
        "confidence": confidence,
        "probabilities": prediction[0].tolist()
    })

if __name__ == "__main__":
    uvicorn.run("handwritting_ai:app", host="0.0.0.0", port=6969, reload=True)
