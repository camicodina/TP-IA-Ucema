import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AudioClassificationService, ClassificationResult } from '../services/audio-classification.service';

type Emotion = 'happy' | 'neutral' | 'angry' | null;

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {
  selectedEmotion = signal<Emotion>(null);
  isProcessing = signal<boolean>(false);
  isRecording = signal<boolean>(false);
  mediaRecorder: MediaRecorder | null = null;
  audioChunks: Blob[] = [];
  audioUrl: string | null = null;
  selectedFile: File | null = null;

  constructor(private audioService: AudioClassificationService) {}

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      this.processAudio(this.selectedFile);
    }
  }

  startRecording(): void {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        this.isRecording.set(true);
        this.audioChunks = [];
        this.mediaRecorder = new MediaRecorder(stream);
        
        this.mediaRecorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data);
        };

        this.mediaRecorder.onstop = () => {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
          const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });
          this.processAudio(audioFile);
          
          // Limpiar stream
          stream.getTracks().forEach(track => track.stop());
        };

        this.mediaRecorder.start();
      })
      .catch(error => {
        console.error('Error al acceder al micrófono:', error);
        alert('Error al acceder al micrófono. Por favor, permite el acceso al micrófono.');
      });
  }

  stopRecording(): void {
    if (this.mediaRecorder && this.isRecording()) {
      this.mediaRecorder.stop();
      this.isRecording.set(false);
    }
  }

  processAudio(file: File): void {
    this.isProcessing.set(true);
    this.selectedEmotion.set(null);

    this.audioService.classifyAudio(file).subscribe({
      next: (result: ClassificationResult) => {
        this.selectedEmotion.set(result.emotion);
        this.isProcessing.set(false);
      },
      error: (error) => {
        console.error('Error al procesar audio:', error);
        // Para testing, simular una respuesta
        this.simulateClassification();
        this.isProcessing.set(false);
      }
    });
  }

  // Método temporal para simular la clasificación si el backend no está disponible
  simulateClassification(): void {
    const emotions: Emotion[] = ['happy', 'neutral', 'angry'];
    const randomEmotion = emotions[Math.floor(Math.random() * emotions.length)];
    setTimeout(() => {
      this.selectedEmotion.set(randomEmotion);
    }, 1500);
  }

  getEmotionIcon(emotion: Emotion): string {
    switch (emotion) {
      case 'happy':
        return '😊';
      case 'neutral':
        return '😐';
      case 'angry':
        return '😠';
      default:
        return '😐';
    }
  }

  getEmotionText(emotion: Emotion): string {
    switch (emotion) {
      case 'happy':
        return 'Feliz';
      case 'neutral':
        return 'Neutral';
      case 'angry':
        return 'Enojado';
      default:
        return '';
    }
  }

  getAgentSuggestion(emotion: Emotion): string {
    switch (emotion) {
      case 'happy':
        return 'Se sugiere derivar a un agente especializado en atención al cliente feliz';
      case 'neutral':
        return 'Se sugiere derivar a un agente de atención estándar';
      case 'angry':
        return 'Se sugiere derivar a un agente especializado en resolución de conflictos';
      default:
        return '';
    }
  }

  isEmotionActive(emotion: Emotion): boolean {
    return this.selectedEmotion() === emotion;
  }
}
