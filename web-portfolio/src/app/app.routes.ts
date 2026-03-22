import { Routes } from '@angular/router';
import { Login } from './login/login';
import { DashboardComponent } from './dashboard/dashboard';
import { AuthGuard } from './auth-guard';
import { Redirect } from './redirect/redirect';
import { GoldChartComponent } from './gold-chart/gold-chart.component'

export const routes: Routes = [
    { path: '', component: Redirect },
    { path: 'login', component: Login },
    { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
    { path: 'gold-chart', component: GoldChartComponent },
];