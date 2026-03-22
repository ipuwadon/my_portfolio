import { Component, OnInit } from '@angular/core';
import { jwtDecode } from 'jwt-decode';
import { SkillService } from '../skill.service';
import { CommonModule } from '@angular/common';
import { ChangeDetectorRef } from '@angular/core';
import { Skill } from '../models/skill.model';
import { GoldChartComponent } from '../gold-chart/gold-chart.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, GoldChartComponent],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css'],
})
export class DashboardComponent implements OnInit{
  message: string = "My pleasure to be here!!";
  userEmail: string | null = null;
  skills: Skill[] = [];

  constructor(private skillService: SkillService, private cd: ChangeDetectorRef){}

  ngOnInit(): void {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded: any = jwtDecode(token);
        this.userEmail = decoded.sub;
      } catch (error) {
        console.error("Invalid token", error);
      }
    }

    this.skillService.getSkills().subscribe({
      next: (data) => {
        console.log("Skills received:", data);
        this.skills = data;
        this.cd.detectChanges();
      },
      error: (err) => console.error("Error fetching skills:", err)
    });
  }

  decodeLevel(level: string): string {
    switch (level) {
      case 'H': return 'High';
      case 'M': return 'Midium';
      case 'L': return 'Low';
      default: return level;
    }
  }
}