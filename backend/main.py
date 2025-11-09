from fastapi import FastAPI, File, UploadFile
from fastai.vision.all import *
import librosa
import numpy as np
import matplotlib.pyplot as plt
import io

app = FastAPI()

# Cargar el modelo al iniciar la app
learn_inf = load_learner('contact_center_model.pkl')

# Replicar tu función de prioridad
def get_priority(emotion):
    if emotion in ['angry', 'fearful', 'disgust']:
        return "ALTA"
    elif emotion in ['sad', 'surprised']:
        return "MEDIA"
    else:
        return "BAJA"

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # 1. Guardar audio temporalmente o cargarlo en memoria
    contents = await file.read()
    with open("temp.wav", "wb") as f:
        f.write(contents)

    # 2. Preprocesamiento (IGUAL QUE EN TU NOTEBOOK)
    y, sr = librosa.load("temp.wav")
    y_trimmed, _ = librosa.effects.trim(y, top_db=25)
    D = librosa.feature.melspectrogram(y=y_trimmed, sr=sr, n_mels=128)
    S_db = librosa.power_to_db(D, ref=np.max)

    # 3. Generar imagen en memoria (sin guardar a disco si es posible para eficiencia)
    plt.figure(figsize=(4, 3))
    librosa.display.specshow(S_db, sr=sr)
    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='jpg', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close()

    # 4. Inferencia con FastAI
    pred_class, pred_idx, outputs = learn_inf.predict(buf.read())
    confidence = float(outputs[pred_idx])

    return {
        "emotion": str(pred_class),
        "priority": get_priority(str(pred_class)),
        "confidence": confidence
    }