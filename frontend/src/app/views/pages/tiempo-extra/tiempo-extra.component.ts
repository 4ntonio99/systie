import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/service/auth.service';
//import { EmpleadoTiempoExtraComponent } from './views/empleado-view/empleado-tiempo-extra.component';
import { EncargadoTiempoExtraComponent } from './views/encargado-view/encargado-tiempo-extra.component';

@Component({
  selector: 'app-tiempo-extra',
  standalone: true,
  imports: [
    CommonModule,
    EncargadoTiempoExtraComponent
  ],
  templateUrl: './tiempo-extra.component.html',
  styleUrls: ['./tiempo-extra.component.css']
})
export class TiempoExtraComponent {
  private authService = inject(AuthService);
  usuario = this.authService.getInfoUsuario();

  // Validamos según el nivel del usuario para decidir qué vista renderizar
  get esEmpleado(): boolean {
    return this.usuario?.nivel === 'empleado'; // Ajusta el string según lo que devuelva tu backend
  }

  get esEncargadoOAdmin(): boolean {
    return this.usuario?.nivel === 'encargado' || this.usuario?.nivel === 'admin';
  }
}