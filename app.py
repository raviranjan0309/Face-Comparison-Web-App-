import os
import glob
import base64
import dlib
import scipy.misc
import numpy as np
import  _thread
import time

# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, make_response
from werkzeug import secure_filename
# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER_IMAGE'] = 'uploads/image/'
app.config['UPLOAD_FOLDER_ID'] = 'uploads/id/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg'])
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')

# Route that will process the file upload Image
@app.route('/uploadImage', methods=['POST'])
def uploadImage():
    # Get the name of the uploaded file
    file = request.values['imageBase64']
    imgdata = base64.b64decode(file)
    filename = str(len(os.listdir(app.config['UPLOAD_FOLDER_IMAGE'])) + 1) + '.jpg'
    filepath = os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], filename)
    with open(filepath, 'wb') as f:
        f.write(imgdata)
    # headers = {'Content-Type': 'text/html'}
    return (render_template('idUpload.html'))


# Route that will process the file upload ID image
@app.route('/uploadId', methods=['POST'])
def uploadId():
    # Get the name of the uploaded file
    file = request.values['imageBase64']
    imgdata = base64.b64decode(file)
    filename = str(len(os.listdir(app.config['UPLOAD_FOLDER_ID'])) + 1) + '.jpg'
    filepath = os.path.join(app.config['UPLOAD_FOLDER_ID'], filename)
    with open(filepath, 'wb') as f:
        f.write(imgdata)

face_detector = dlib.get_frontal_face_detector()

shape_predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

face_recognition_model = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')

TOLERANCE = 0.5

def get_face_encodings(path_to_image):
    image = scipy.misc.imread(path_to_image)
    # The 1 in the second argument indicates that we should upsample the image
    # 1 time.  This will make everything bigger and allow us to detect more
    # faces.
    detected_faces = face_detector(image, 1)
    shapes_faces = [shape_predictor(image, face) for face in detected_faces]
    return [np.array(face_recognition_model.compute_face_descriptor(image, face_pose, 1)) for face_pose in shapes_faces]

def compare_face_encodings(known_faces, face):
    disimilarity = np.linalg.norm(known_faces - face, axis=1)
    result = disimilarity <= TOLERANCE
    return (disimilarity,result)


# Route that will process the file upload
@app.route('/verify', methods=['POST'])
def upload():
    image_one = max(glob.glob(r'uploads/image/*.jpg'), key=os.path.getctime)
    print(image_one)
    image_two = max(glob.glob(r'uploads/id/*.jpg'), key=os.path.getctime)
    print(image_two)
    image_one_encode = get_face_encodings(image_one)
    image_two_encode = get_face_encodings(image_two)
    disimilarity, result = compare_face_encodings(image_one_encode,image_two_encode[0])
    if result:
        if(disimilarity < 1.00):
            # y = -100 * disimilarity + 100
            conf = (1-disimilarity)
            label_text = 'Image Matched with similarity confidence of ' + ' '.join(map(str, conf))
            return render_template('result.html', text=label_text, file1= image_one, file2 = image_two)
    else:
        if(disimilarity < 1.00):
            conf = (disimilarity)
            label_text = 'Image Not Matched with dissimilarity confidence of ' + ' '.join(map(str, conf))
            return render_template('result.html', text=label_text, file1=image_one, file2=image_two)



# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def cleanDirectory(threadName,delay):

   while True:
       time.sleep(delay)
       print ("Cleaning Up Directory")
       fileuploadlist = [ f for f in (os.listdir(app.config['UPLOAD_FOLDER_IMAGE']))  ]
       fileidlist = [f for f in (os.listdir(app.config['UPLOAD_FOLDER_ID']))]
       for f in fileuploadlist:
         #os.remove("Uploads/"+f)
         os.remove(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], f))
       for f in fileidlist:
           # os.remove("Uploads/"+f)
           os.remove(os.path.join(app.config['UPLOAD_FOLDER_ID'], f))


if __name__ == '__main__':
    try:
       _thread.start_new_thread( cleanDirectory, ("Cleaning Thread", 300, ) )
    except:
       print("Error: unable to start thread" )
    app.run()
