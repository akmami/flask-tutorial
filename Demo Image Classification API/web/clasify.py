from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import requests

model = ResNet50(weights='imagenet')

def clasify(url):
    r = requests.get(url)
    with open('temp.jpg', 'wb') as f:
        f.write(r.content)
        
        img = image.load_img('temp.jpg', target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        
        preds = model.predict(x)
        top3 = decode_predictions(preds, top=3)[0]
        return (top3[0][1], float(top3[0][2]))
