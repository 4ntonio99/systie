import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { BaseComponent } from './views/layout/base/base.component';

export const routes: Routes = [
  // 1. Vista pública de Login
  {
    path: 'auth',
    loadChildren: () => import('./views/pages/auth/auth.routes').then(m => m.AUTH_ROUTES)
  },

  // 2. Vistas protegidas bajo el Layout Principal
  {
    path: '',
    component: BaseComponent,
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        // Asegúrate de que apunte a tu componente o módulo del dashboard:
        loadComponent: () => import('./views/pages/dashboard/dashboard.component').then(m => m.DashboardComponent)
        // O si usas lazy loading por rutas:
        // loadChildren: () => import('./views/pages/dashboard/dashboard.routes').then(m => m.DASHBOARD_ROUTES)
      },
      {
        path: 'TiempoExtra',
        // Asegúrate de que apunte a tu componente o módulo del dashboard:
        loadComponent: () => import('./views/pages/tiempo-extra/tiempo-extra.component').then(m => m.TiempoExtraComponent)
        // O si usas lazy loading por rutas:
        // loadChildren: () => import('./views/pages/dashboard/dashboard.routes').then(m => m.DASHBOARD_ROUTES)
      },
      // Redirección por defecto al entrar a la app
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      }
    ]
  }
];