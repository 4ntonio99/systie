import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../../core/service/auth.service';

@Component({
  selector: 'app-base',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './base.component.html',
  styleUrls: ['./base.component.css']
})
export class BaseComponent {
  private authService = inject(AuthService);
  usuario = this.authService.getInfoUsuario();

  // Verificamos si el usuario es administrador (ajusta la condición según tu objeto, por ejemplo: rol === 'admin')
  get esAdmin(): boolean {
    return this.usuario?.rol === 'admin' || this.usuario?.nivel === 'admin';
  }

  logout() {
    localStorage.removeItem('token');
    window.location.href = '/auth';
  }
}