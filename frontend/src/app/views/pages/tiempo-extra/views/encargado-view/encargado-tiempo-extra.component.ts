import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { AuthService } from '../../../../../core/service/auth.service';

@Component({
  selector: 'app-encargado-tiempo-extra',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './encargado-tiempo-extra.component.html',
  styleUrls: ['./encargado-tiempo-extra.component.css']
})
export class EncargadoTiempoExtraComponent {
  private authService = inject(AuthService);
  private http = inject(HttpClient);
  
  usuario = this.authService.getInfoUsuario();

  // Verificamos si el usuario es administrador
  get esAdmin(): boolean {
    return this.usuario?.rol === 'admin' || this.usuario?.nivel === 'admin';
  }

  logout() {
    localStorage.removeItem('token');
    window.location.href = '/auth';
  }

  descargarReporte() {
    const hoy = new Date();
    const mes = hoy.getMonth() + 1; // 1 a 12
    const dia = hoy.getDate();      // 1 a 31

    // 1. Identificar la quincena actual (1 a 24)
    let quincenaActual = (mes - 1) * 2 + (dia <= 15 ? 1 : 2);

    // 2. Restar una quincena (queremos la quincena anterior)
    let quincenaAnterior = quincenaActual - 1;

    // 3. Ajuste si estamos en enero y bajamos de la quincena 1 -> quincena 24 del año previo
    if (quincenaAnterior < 1) {
      quincenaAnterior = 24;
    }

    console.log(`Fecha actual: ${dia}/${mes} -> Quincena calculada a enviar: ${quincenaAnterior}`);

    // 4. Configurar headers con el token y parámetros para la petición HTTP
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    const params = new HttpParams().set('quincena', quincenaAnterior.toString());

    // 5. Ejecutar la petición al endpoint de FastAPI esperando un Blob (archivo binario/texto)
    this.http.get('http://localhost:8000/tiempo-extra/reporte-area-txt', {
      headers,
      params,
      responseType: 'blob'
    }).subscribe({
      next: (blobResponse) => {
        const blob = new Blob([blobResponse], { type: 'text/plain;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        
        // Simular un enlace de descarga en el navegador
        const link = document.createElement('a');
        link.href = url;
        link.download = `reporte_tiempo_extra_quincena_${quincenaAnterior}.txt`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        console.error('Error al descargar el reporte:', err);
      }
    });
  }
}