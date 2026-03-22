import { Component, OnInit } from '@angular/core';
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Legend } from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';
import { GoldPriceService } from '../gold-price.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

Chart.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Legend, zoomPlugin);

@Component({
  selector: 'app-gold-chart',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './gold-chart.component.html',
  styleUrls: ['./gold-chart.component.css']
})
export class GoldChartComponent implements OnInit {
  historicalChart: any;
  predictiveChart: any;
  rawData: any[] = [];

  selectedYear: string = '2020';
  selectedMonth: string = 'ALL';

  years: string[] = [];
  months: string[] = [];

  constructor(private goldService: GoldPriceService) {}

  ngOnInit() {
    this.goldService.getGoldPrices().subscribe(history => {
      this.rawData = history;

      // Extract unique years and months
      this.years = [...new Set(history.map(d => d.year))];
      this.months = ['ALL', ...new Set(history.map(d => d.month))];

      // Filter by default year
      let filtered = this.rawData.filter(d => d.year === this.selectedYear);

      // Build historical chart
      this.buildHistoricalChart(filtered);

      // Fetch forecast (next 10 days) and build predictive chart
      this.goldService.getGoldPriceForecast(10).subscribe(res => {
        this.buildPredictiveChart(res.forecast);
      });
    });
  }

  buildHistoricalChart(history: any[]) {
    const dates = history.map(d => d.date);
    const buyPrices = history.map(d => d.gold_bar_buy);
    const sellPrices = history.map(d => d.gold_bar_sell);
    const spotPrices = history.map(d => d.gold_spot);

    const ctx = document.getElementById('goldChart') as HTMLCanvasElement;

    if (this.historicalChart) {
      this.historicalChart.destroy();
    }

    this.historicalChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [
          { label: 'Buy Price', data: buyPrices, borderColor: 'green', borderWidth: 1, fill: false },
          { label: 'Sell Price', data: sellPrices, borderColor: 'red', borderWidth: 1, fill: false },
          { label: 'Spot Price', data: spotPrices, borderColor: 'blue', borderWidth: 1, fill: false }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' },
          zoom: {
            zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' },
            pan: { enabled: true, mode: 'x' }
          }
        }
      },
      plugins: [{
        id: 'historicalBackground',
        beforeDraw: (chart) => {
          const { ctx, chartArea } = chart;
          ctx.save();
          ctx.fillStyle = '#fceec6'; // light beige for history
          ctx.fillRect(chartArea.left, chartArea.top, chartArea.width, chartArea.height);
          ctx.restore();
        }
      }]
    });
  }

  buildPredictiveChart(forecast: any[]) {
    const forecastDates = forecast.map(d => d.ds.split('T')[0]);
    const forecastPredictions = forecast.map(d => d.yhat);
    const forecastLower = forecast.map(d => d.yhat_lower);
    const forecastUpper = forecast.map(d => d.yhat_upper);

    const ctx = document.getElementById('goldPredictiveChart') as HTMLCanvasElement;

    if (this.predictiveChart) {
      this.predictiveChart.destroy();
    }

    this.predictiveChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: forecastDates,
        datasets: [
          {
            label: 'Predicted Price',
            data: forecastPredictions,
            borderColor: 'orange',
            borderDash: [5, 5],
            borderWidth: 2,
            fill: false
          },
          {
            label: 'Lower Bound',
            data: forecastLower,
            borderColor: 'gray',
            borderDash: [2, 2],
            borderWidth: 1,
            fill: false
          },
          {
            label: 'Upper Bound',
            data: forecastUpper,
            borderColor: 'gray',
            borderDash: [2, 2],
            borderWidth: 1,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' },
          zoom: {
            zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' },
            pan: { enabled: true, mode: 'x' }
          }
        }
      },
      plugins: [{
        id: 'predictiveBackground',
        beforeDraw: (chart) => {
          const { ctx, chartArea } = chart;
          ctx.save();
          ctx.fillStyle = '#fceec6'; // dark teal for forecast
          ctx.fillRect(chartArea.left, chartArea.top, chartArea.width, chartArea.height);
          ctx.restore();
        }
      }]

    });
  }

  updateChart() {
    let filtered = this.rawData;

    if (this.selectedYear) {
      filtered = filtered.filter(d => d.year === this.selectedYear);
    }

    if (this.selectedMonth && this.selectedMonth !== 'ALL') {
      filtered = filtered.filter(d => d.month === this.selectedMonth);
    }

    this.buildHistoricalChart(filtered);
  }

  resetZoom() {
    if (this.historicalChart) {
      this.historicalChart.resetZoom();
    }
    if (this.predictiveChart) {
      this.predictiveChart.resetZoom();
    }
  }
}