import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { provideRouter } from '@angular/router';
import { routes } from './app/app.routes';
import { Component, provideZonelessChangeDetection } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `<router-outlet></router-outlet>`
})
class AppRootComponent {}

bootstrapApplication(AppRootComponent, {
  ...appConfig,
  providers: [
    provideZonelessChangeDetection(), // <-- Indicativo sin Zone.js
    ...(appConfig.providers || []),
    provideRouter(routes)
  ]
})
.catch((err) => console.error(err));