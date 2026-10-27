let aspectChartInstance = null;
let trustChartInstance = null;
let comparisonChartInstance = null;

function renderAspectChart(aspectData) {
  const canvas = document.getElementById('aspectChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const labels = Object.keys(aspectData || {});
  const values = Object.values(aspectData || {});

  if (aspectChartInstance) {
    aspectChartInstance.destroy();
    aspectChartInstance = null;
  }

  aspectChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels.map(l => l.replace(/_/g, ' ')),
      datasets: [{
        data: values,
        backgroundColor: ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b'],
        borderColor: '#1e293b',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      animations: {
        colors: false,
        x: false
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#94a3b8', font: { family: 'Inter' } }
        }
      }
    }
  });
}

function renderTrustChart(trustData) {
  const canvas = document.getElementById('trustChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const labels = Object.keys(trustData || {});
  const values = Object.values(trustData || {});

  if (trustChartInstance) {
    trustChartInstance.destroy();
    trustChartInstance = null;
  }

  trustChartInstance = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels.map(l => l.replace(/_/g, ' ')),
      datasets: [{
        data: values,
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        borderColor: '#1e293b',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      animations: {
        colors: false,
        x: false
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#94a3b8', font: { family: 'Inter' } }
        }
      }
    }
  });
}

function renderComparisonChart() {
  const ctx = document.getElementById('comparisonChart').getContext('2d');

  if (comparisonChartInstance) comparisonChartInstance.destroy();

  comparisonChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Akurasi Kepercayaan (Trust)', 'Macro F1 Kepercayaan', 'Akurasi Aspek Komunikasi', 'Macro F1 Aspek'],
      datasets: [
        {
          label: 'IndoBERT Transformer (Fine-Tuned) - 837 Data Uji (test.csv)',
          data: [0.9420, 0.9395, 0.9180, 0.9150],
          backgroundColor: [
            'rgba(15, 118, 110, 0.85)',
            'rgba(16, 185, 129, 0.85)',
            'rgba(13, 148, 136, 0.85)',
            'rgba(5, 150, 105, 0.85)'
          ],
          borderColor: '#0F766E',
          borderWidth: 2,
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 1.0,
          grid: { color: 'rgba(0, 0, 0, 0.05)' },
          ticks: {
            color: '#64748b',
            callback: function(val) { return (val * 100) + '%'; }
          }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#334155', font: { weight: '600' } }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#0F766E', font: { family: 'Plus Jakarta Sans', weight: '700' } }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return ` Skor: ${(context.raw * 100).toFixed(2)}%`;
            }
          }
        }
      }
    }
  });
}
