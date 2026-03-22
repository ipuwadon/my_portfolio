import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Injectable } from '@angular/core';
import { jwtDecode } from 'jwt-decode';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private router: Router) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot 
  ): boolean {
    const token = localStorage.getItem('token')
    console.log('Token from localStorage:', token);

    if (token) {
      try {
        const decoded: any = jwtDecode(token);
        const now = Math.floor(Date.now() / 1000);
        console.log('Decoded token:', decoded);
        console.log('Current time:', now);
        console.log('Token expiry:', decoded.exp);

        if (decoded.exp && decoded.exp > now) {
          console.log('Token is valid');
          return true;
        } else {
          console.log('Token expired');
        }
      } catch (error) {
        console.error('Invalid token', error);
      }
    }
    this.router.navigate(['/login']);
    return false;
  }
}
