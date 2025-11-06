# Analizador de Audio Restnest - Componente Home

## Configuración

### 1. Logo
- Coloca tu logo en la carpeta `public/` con el nombre `logo.png`
- El logo se mostrará automáticamente en el header izquierdo

### 2. Backend/Colab
- El servicio está configurado para conectarse a: `http://localhost:8000/api/classify-audio`
- Para cambiar la URL, edita `src/app/services/audio-classification.service.ts` línea 12

### 3. Formato de respuesta esperado del backend
El backend debe responder con un JSON con el siguiente formato:
```json
{
  "emotion": "happy" | "neutral" | "angry",
  "confidence": 0.95  // opcional
}
```

### 4. Testing sin backend
Si el backend no está disponible, la aplicación simulará una respuesta aleatoria para testing.

## Uso

1. **Subir Audio**: Haz clic en "Subir Audio" y selecciona un archivo de audio desde tu PC
2. **Grabar Audio**: Haz clic en "Grabar" para grabar audio en tiempo real (requiere permisos de micrófono)
3. **Resultado**: Después de procesar, se iluminará la carita correspondiente a la emoción detectada
4. **Sugerencia**: Se mostrará una sugerencia de derivación a un agente según la emoción detectada

## Estructura de Archivos

```
src/app/
├── home/
│   ├── home.component.ts      # Lógica del componente
│   ├── home.component.html    # Template HTML
│   └── home.component.scss    # Estilos
├── services/
│   └── audio-classification.service.ts  # Servicio para comunicarse con el backend
└── app.component.ts           # Componente principal que usa Home

public/
└── logo.png                   # Logo (debes agregarlo)
```
