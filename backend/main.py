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
BASE_DIR = Path(__file__).parent.absolute()
MODEL_PATH = BASE_DIR.parent / "model" / "contact_center_model.pkl"

# Cargar el modelo al iniciar la app
learn_inf = None
model_load_error = None
model_load_traceback = None

try:
    # Convertir a ruta absoluta y string
    model_path_str = str(MODEL_PATH.absolute())
    
    # Verificar que el archivo existe
    if not MODEL_PATH.exists():
        error_msg = f"ERROR: El archivo del modelo no existe en: {model_path_str}"
        model_load_error = error_msg
    else:
        
        # Intentar cargar el modelo con la ruta como string
        import sys
        import traceback as tb_module
        import pathlib
        import pickle
        from pathlib import WindowsPath
        
        try:
            # Monkey-patch para convertir PosixPath a WindowsPath durante la deserialización
            # Esto es necesario porque el modelo fue entrenado en Linux pero se carga en Windows
            # Creamos una clase compatible que herede de WindowsPath
            class PosixPathCompat(WindowsPath):
                pass
            
            # Hacer el patch en el módulo pathlib antes de que pickle lo necesite
            # Guardar el valor original si existe
            original_posix_path = None
            if hasattr(pathlib, 'PosixPath'):
                try:
                    original_posix_path = pathlib.PosixPath
                except (AttributeError, OSError):
                    # PosixPath no está disponible en Windows, eso está bien
                    pass
            
            # Reemplazar PosixPath en el módulo pathlib
            pathlib.PosixPath = PosixPathCompat
            
            # También hacer el patch en sys.modules para que pickle lo encuentre
            if 'pathlib' in sys.modules:
                sys.modules['pathlib'].PosixPath = PosixPathCompat
            
            try:
                learn_inf = load_learner(model_path_str)
            finally:
                # Restaurar PosixPath original si existía
                if original_posix_path is not None:
                    pathlib.PosixPath = original_posix_path
                    if 'pathlib' in sys.modules:
                        sys.modules['pathlib'].PosixPath = original_posix_path
                else:
                    # Si no existía, intentar eliminarlo
                    try:
                        if hasattr(pathlib, 'PosixPath'):
                            delattr(pathlib, 'PosixPath')
                        if 'pathlib' in sys.modules and hasattr(sys.modules['pathlib'], 'PosixPath'):
                            delattr(sys.modules['pathlib'], 'PosixPath')
                    except:
                        pass
                
        except Exception as load_error:
            # Asegurarse de restaurar PosixPath original incluso si hay error
            if 'original_posix_path' in locals() and original_posix_path is not None:
                try:
                    pathlib.PosixPath = original_posix_path
                    if 'pathlib' in sys.modules:
                        sys.modules['pathlib'].PosixPath = original_posix_path
                except:
                    pass
            
            model_load_error = f"{type(load_error).__name__}: {str(load_error)}"
            model_load_traceback = ''.join(tb_module.format_exception(type(load_error), load_error, load_error.__traceback__))
            learn_inf = None
            
except FileNotFoundError as e:
    model_load_error = f"FileNotFoundError: {str(e)}"
    import traceback
    model_load_traceback = ''.join(traceback.format_exc())
    learn_inf = None
except Exception as e:
    model_load_error = f"{type(e).__name__}: {str(e)}"
    import traceback
    model_load_traceback = ''.join(traceback.format_exc())
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
    elif emotion_lower in ['neutral', "calm", "surprised"]:
        return 'neutral'
    elif emotion_lower in ['angry', "sad", "fearful", "disgust"]:
        return 'angry'
    else:
        # Default to neutral for unknown emotions
        return 'neutral'

@app.post("/predict")
@app.post("/api/classify-audio")
async def predict(audio: UploadFile = File(...)):
    if learn_inf is None:
        error_detail = {
            "error": "Modelo no disponible",
            "model_path": str(MODEL_PATH.absolute()),
            "model_exists": MODEL_PATH.exists(),
            "model_loaded": False
        }
        
        if model_load_error:
            error_detail["load_error"] = model_load_error
            error_detail["load_traceback"] = model_load_traceback
        
        raise HTTPException(status_code=500, detail=error_detail)
    
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
            "emotion_str": emotion_str,
            "priority": get_priority(emotion_str),
            "confidence": confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar audio: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass