from flask import Flask, render_template, request
from PIL import Image
import io
import numpy
from functools import wraps

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=['POST'])
def upload_image():
    # get uploaded image
    img = request.files['file']
    if img != "":
        width, height, multiplex, single_row = 88, 88, 2, 5
        image = Image.open(io.BytesIO(img.read()))
        # resize
        image = image.resize((height, width), Image.Resampling.LANCZOS)
        image = image.rotate(180)
        # convert image to numpy 3d array
        data = numpy.asarray(image)
        print(data.shape)
        # iterate through image -> get drawing instruction
        instruction_set = []
        counter = 0
        for section in range(int(width/single_row)):
            instruction = '''sensor draw switch1 @enabled
jump 3 equal draw true
end'''
            for i in range(single_row*section, single_row*(section+1)): # row
                for j in range(width): # col
                    pixel = data[j][i]
                    instruction += f'''
draw rect {i*multiplex if i!=0 else i} {j*multiplex if j!=0 else j} {multiplex} {multiplex} 0 0
draw color {pixel[0]} {pixel[1]} {pixel[2]} 255 0 0'''
                    if (counter >= 20):
                        counter = 0
                        instruction += "\ndrawflush display1"
                    counter += 1
            instruction += f'''
drawflush display1
control enabled switch1 false 0 0 0
    '''
            instruction_set.append(instruction)
        return render_template("result.html", data=instruction_set)
    return "failed"

app.run("0.0.0.0", debug=True)