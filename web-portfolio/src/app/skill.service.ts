import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Skill } from './models/skill.model';

@Injectable({
  providedIn: 'root',
})
export class SkillService {
  private apiUrl = "http://localhost:8000/skills";
  /*private apiUrl = "http://192.168.100.166:8000/skills";*/

  constructor(private http: HttpClient) {}

  getSkills(): Observable<Skill[]> {
    return this.http.get<Skill[]>(this.apiUrl);
  }
}