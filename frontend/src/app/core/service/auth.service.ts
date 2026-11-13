import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000'; 

  login(curp: string, rfc: string): Observable<any> {
    const body = new HttpParams()
      .set('username', curp)
      .set('password', rfc);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    return this.http.post<any>(`${this.apiUrl}/auth/login`, body.toString(), { headers });
  }

  // Método para obtener la info real del usuario logueado en el BaseComponent
  getInfoUsuario() {
    const userJson = localStorage.getItem('user_info');
    if (userJson) {
      return JSON.parse(userJson);
    }
    return {
      nombre: 'Usuario',
      nivel: '',
      adsc: ''
    };
  }
}