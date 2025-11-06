import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';

export interface ClassificationResult {
  emotion: 'happy' | 'neutral' | 'angry';
  confidence?: number;
}

@Injectable({
  providedIn: 'root'
})
export class AudioClassificationService {
  // URL de tu backend/colab - cambiar por la URL real
  private apiUrl = 'http://localhost:8000/api/classify-audio';

  constructor(private http: HttpClient) {}

  classifyAudio(audioFile: File): Observable<ClassificationResult> {
    const formData = new FormData();
    formData.append('audio', audioFile);

    const headers = new HttpHeaders();

    return this.http.post<ClassificationResult>(this.apiUrl, formData, { headers }).pipe(
      catchError(error => {
        console.error('Error al clasificar audio:', error);
        return throwError(() => error);
      })
    );
  }
}
