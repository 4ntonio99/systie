import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/service/auth.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="min-h-screen flex items-center justify-center bg-base-200">
      <div class="card w-full max-w-md shadow-2xl bg-base-100">
        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="card-body">
          
          <div class="text-center mb-2">
            <h2 class="text-3xl font-bold">Bienvenido</h2>
            <p class="text-sm text-base-content/60 mt-1">Ingresa tu CURP y RFC para continuar</p>
          </div>

          <!-- Campo CURP (username) -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">CURP (Usuario)</span>
            </label>
            <input 
              type="text" 
              formControlName="username" 
              placeholder="Ingresa tu CURP" 
              class="input input-bordered w-full uppercase" 
            />
          </div>

          <!-- Campo RFC (password) -->
          <div class="form-control mt-2">
            <label class="label">
              <span class="label-text font-medium">RFC (Contraseña)</span>
            </label>
            <input 
              type="password" 
              formControlName="password" 
              placeholder="Ingresa tu RFC" 
              class="input input-bordered w-full uppercase" 
            />
          </div>

          <!-- Mensaje de Error -->
          @if (errorMessage) {
            <div class="alert alert-error mt-4 py-2 text-sm">
              <span>{{ errorMessage }}</span>
            </div>
          }

          <!-- Botón de Envío -->
          <div class="form-control mt-6">
            <button 
              type="submit" 
              class="btn btn-primary w-full" 
              [disabled]="loginForm.invalid || isLoading">
              @if (isLoading) {
                <span class="loading loading-spinner"></span>
              }
              Iniciar Sesión
            </button>
          </div>

        </form>
      </div>
    </div>
  `
})
export class AuthComponent {
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private authService = inject(AuthService);

  isLoading = false;
  errorMessage = '';

  loginForm: FormGroup = this.fb.group({
    username: ['', [Validators.required]],
    password: ['', [Validators.required]]
  });

  onSubmit() {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = '';
      
      const { username, password } = this.loginForm.value;

      this.authService.login(username, password).subscribe({
        next: (response) => {
          this.isLoading = false;
          
          // 1. Guardamos el token JWT
          localStorage.setItem('token', response.access_token);
          
          // 2. Guardamos el objeto completo del usuario devuelto por FastAPI
          if (response.usuario) {
            localStorage.setItem('user_info', JSON.stringify(response.usuario));
          }

          // 3. Redirigimos al dashboard protegido
          this.router.navigate(['/dashboard']);
        },
        error: (err) => {
          this.isLoading = false;
          this.errorMessage = 'Credenciales incorrectas o error al conectar con el servidor.';
          console.error('Error en login:', err);
        }
      });
    } else {
      this.loginForm.markAllAsTouched();
    }
  }
}