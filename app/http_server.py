import os
import base64
import json
import random
import string
from PIL import Image
from flask import Flask, request, jsonify, make_response
from gevent import pywsgi

from yoloV8 import YOLOProcessor

app = Flask(__name__)

processor = YOLOProcessor()

def convert_to_jpg(file):
    img = Image.open(file)
    img = img.convert('RGB')
    return img

def createKey():
    key_length = 15
    characters = string.ascii_letters + string.digits
    random_key = ''.join(random.choice(characters) for i in range(key_length))
    return random_key

@app.route('/api/v1/process_image/yoloV8', methods=['POST'])
def picture():
    try:
        key = createKey()

        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier trouvé'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        extension = os.path.splitext(file.filename)[1].lower()
        if extension == '.png':
            image = convert_to_jpg(file)
        elif extension not in ['.jpg', '.jpeg', '.webp']:
            return jsonify({'error': 'Invalide format'}), 400
        else:
            image = Image.open(file)

        accuracy = float(request.form.get('accuracy', 0))
        accuracy = max(0, min(accuracy, 1))

        max_det = request.form.get('max_det', '20')
        max_det = int(max_det) if max_det.isdigit() else 20

        model = request.form.get('version', '1')
        model = model if model in ['1', '2', '3', '4', '5'] else '1'

        task = request.form.get('task', 'detect')
        task = task if task in ['detect', 'segmen', 'pose', 'obb'] else 'detect'

        score = request.form.get('score', 'off')
        score = score if score in ['on', 'off'] else 'off'

        jsonData = processor.process_image(image, accuracy, model, task, score, max_det, key)

        with open(f"tmp/output/image/{key}.jpg", "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        response_data = {
            "file_data": encoded_image,
            "json_data": jsonData
        }

        response = make_response(json.dumps(response_data))
        response.headers['Content-Type'] = 'application/json'
        os.remove(f"tmp/output/image/{key}.jpg")

        return response

    except Exception as e:
        error = "Erreur lors du traitement de l'image: " + str(e)
        return jsonify({'error': error}), 500

@app.route('/api/v1/process_video/yoloV8', methods=['POST'])
def video():
    try:
        key = createKey()

        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier trouvé'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        extension = os.path.splitext(file.filename)[1].lower()
        if extension not in ['.mp4', '.avi', '.webm', '.mkv']:
            return jsonify({'error': 'Invalide format'}), 400
        else:
            os.makedirs("tmp/input/video", exist_ok=True)
            file_path = f"tmp/input/video/{key}{extension}"
            file.save(file_path)
            video = file_path

        accuracy = float(request.form.get('accuracy', 0))
        accuracy = max(0, min(accuracy, 1))

        max_det = request.form.get('max_det', '20')
        max_det = int(max_det) if max_det.isdigit() else 20

        model = request.form.get('version', '1')
        model = model if model in ['1', '2', '3', '4', '5'] else '1'

        task = request.form.get('task', 'detect')
        task = task if task in ['detect', 'segmen', 'pose', 'obb'] else 'detect'

        score = request.form.get('score', 'off')
        score = score if score in ['on', 'off'] else 'off'

        jsonData = processor.process_video(video, accuracy, model, task, score, max_det, key)

        with open(f"tmp/output/video/{key}.mp4", "rb") as video_file:
            encoded_video = base64.b64encode(video_file.read()).decode('utf-8')

        response_data = {
            "file_data": encoded_video,
            "json_data": jsonData
        }

        response = make_response(json.dumps(response_data))
        response.headers['Content-Type'] = 'application/json'

        os.remove(f"tmp/output/video/{key}.mp4")
        os.remove(file_path)

        return response

    except Exception as e:
        error = "Erreur lors du traitement de la vidéo: " + str(e)
        return jsonify({'error': error}), 500

if __name__ == "__main__":
    http_server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    print("HTTP server running on port 5000")
    http_server.serve_forever()
    
