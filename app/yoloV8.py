import json
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import os
import imageio

# Chemin d'accès aux fichiers de sortie
output_path = "tmp/output/"
model_path = "models/"
modelsDico = {"1": 'yolov8n', "2": 'yolov8s', "3": 'yolov8m', "4": 'yolov8l', "5": 'yolov8x'}
taskDico = {"detect": '', "segmen": '-seg', "pose": '-pose', "obb": '-obb'}

class YOLOProcessor:
    def __init__(self):
        self.models = {}
        for version in modelsDico:
            for task in taskDico:
                model_name = str(model_path + modelsDico[version] + taskDico[task] + ".pt")
                self.models[(version, task)] = YOLO(model_name)

    def process_image(self, image, accuracy, version, task, score, max_det, key):
        try:
            score = True if score == 'on' else False
            model = self.models[(version, task)]
            image_copy = np.asarray(image).copy()
            results = model(image_copy, conf=accuracy, max_det=max_det)
            jsonData = results[0].tojson(normalize=False, decimals=5)
            self._process_results(results, score, key, None)
            return jsonData
        except Exception as e:
            print("image_process: Error: ", e)
            return None

    def process_image_webcam(self, image):
        try:
            accuracy = 0.5
            max_det = 20
            model = '1'
            task = 'detect'
            model = self.models[(model, task)]
            results = model(image, conf=accuracy, max_det=max_det)
            jsonData = results[0].tojson(normalize=False, decimals=5)
            return jsonData
        except Exception as e:
            print("image_process_webcam: Error: ", e)
            return None

    def process_video(self, video, accuracy, version, task, score, max_det, key):
        try:
            score = True if score == 'on' else False
            model = self.models[(version, task)]
            results = model(video, conf=accuracy, max_det=max_det)
            jsonData = [r.tojson(normalize=False, decimals=5) for r in results]
            jsonData = json.dumps(jsonData)
            self._process_results(results, score, key, video)
            return jsonData
        except Exception as e:
            return None
        

    def _process_results(self, results, score, key, video):
        try:
            if video is None:
                r = results[0]
                
                im_bgr = r.plot(conf=score)
                im_rgb = cv2.cvtColor(im_bgr, cv2.COLOR_BGR2RGB)

                cv2.imwrite(output_path + f"image/{key}.jpg", im_rgb)

            else:
                cap = cv2.VideoCapture(video)
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                fourcc = cv2.VideoWriter_fourcc(*'vp09')
                out = cv2.VideoWriter(output_path + f"video/{key}.mp4", fourcc, fps, (width, height))

                os.chmod(output_path + f"video/{key}.mp4", 0o777)

                for r in results:
                    im_bgr = r.plot(conf=score)
                    out.write(im_bgr)

                out.release()
                cap.release()

        except Exception as e:
            print("pic_process: Error: ", e)
            return None
        
