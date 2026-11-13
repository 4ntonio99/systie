import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TiempoExtraService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000'; // Tu backend de FastAPI

  descargarReporteAreaTxt(quincena: number): Observable<Blob> {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    
    // Pasamos la quincena como query param (?quincena=X)
    const params = new HttpParams().set('quincena', quincena.toString());

    // responseType: 'blob' es vital para que Angular sepa que es un archivo y no texto plano JSON
    return this.http.get(`${this.apiUrl}/tiempo-extra/reporte-area-txt`, {
      headers,
      params,
      responseType: 'blob'
    });
  }
}