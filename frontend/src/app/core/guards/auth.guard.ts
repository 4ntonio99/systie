import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  
  // Validamos si existe el token en localStorage
  const token = localStorage.getItem('token');

  if (token) {
    return true;
  }

  // Si no hay token, retornamos un UrlTree para redirigir limpiamente al login
  return router.createUrlTree(['/auth']);
};