import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GoldPriceService {
  private apiUrl = 'http://127.0.0.1:8000/gold-prices';
  private apiUrlPredict = 'http://127.0.0.1:8000/gold-prices-predictive';


  constructor(private http: HttpClient) {}

  getGoldPrices(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  getGoldPriceForecast(periods: number = 10): Observable<{ forecast: any[] }> {
    return this.http.get<{ forecast: any[] }>(`${this.apiUrlPredict}?periods=${periods}`);
  }
}
