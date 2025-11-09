from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastai.vision.all import *
import librosa
import numpy as np
import matplotlib.pyplot as plt
import io
import os
from pathlib import Path

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the correct path to the model
BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR.parent / "model" / "contact_center_model.pkl"

# Cargar el modelo al iniciar la app
try:
    learn_inf = load_learner(MODEL_PATH)
    print(f"Modelo cargado exitosamente desde: {MODEL_PATH}")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    learn_inf = None

# Replicar tu función de prioridad
def get_priority(emotion):
    if emotion in ['angry', 'fearful', 'disgust']:
        return "ALTA"
    elif emotion in ['sad', 'surprised']:
        return "MEDIA"
    else:
        return "BAJA"

def map_emotion_to_frontend(emotion: str) -> str:
    """Map backend emotion names to frontend expected values"""
    emotion_lower = emotion.lower()
    if emotion_lower in ['happy', 'happiness']:
        return 'happy'
    elif emotion_lower in ['neutral']:
        return 'neutral'
    elif emotion_lower in ['angry', 'anger']:
        return 'angry'
    else:
        # Default to neutral for unknown emotions
        return 'neutral'

@app.post("/predict")
@app.post("/api/classify-audio")
async def predict(audio: UploadFile = File(...)):
    if learn_inf is None:
        raise HTTPException(status_code=500, detail="Modelo no disponible")
    
    temp_file_path = None
    try:
        # 1. Guardar audio temporalmente o cargarlo en memoria
        contents = await audio.read()
        temp_file_path = "temp.wav"
        with open(temp_file_path, "wb") as f:
            f.write(contents)

        # 2. Preprocesamiento (IGUAL QUE EN TU NOTEBOOK)
        y, sr = librosa.load(temp_file_path)
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
        emotion_str = str(pred_class)
        
        # Map emotion to frontend expected format
        mapped_emotion = map_emotion_to_frontend(emotion_str)

        return {
            "emotion": mapped_emotion,
            "priority": get_priority(emotion_str),
            "confidence": confidence
        }
    except Exception as e:
        print(f"Error al procesar audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar audio: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Error al eliminar archivo temporal: {e}")