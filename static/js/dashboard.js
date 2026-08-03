document.addEventListener('DOMContentLoaded', function () {
    // Use Jinja-injected stats instead of a broken API call
    const stats = window.DEVTRACE_STATS;
    if (stats && stats.platforms) {
        const d = stats.platforms;
        const total = (d.github_count || 0) + (d.linkedin_count || 0) +
                      (d.leetcode_count || 0) + (d.hackerrank_count || 0);
        if (total > 0) {
            renderPlatformChart(d);
        }
    }
});

function renderPlatformChart(platforms) {
    const ctx = document.getElementById('platformDistributionChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['GitHub', 'LinkedIn', 'LeetCode', 'HackerRank'],
            datasets: [{
                data: [
                    platforms.github_count || 0,
                    platforms.linkedin_count || 0,
                    platforms.leetcode_count || 0,
                    platforms.hackerrank_count || 0
                ],
                backgroundColor: [
                    'rgba(255,255,255,0.85)',
                    '#0A66C2',
                    '#FFA116',
                    '#2EC4B6'
                ],
                borderColor: 'rgba(255,255,255,0.04)',
                borderWidth: 2,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '68%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94A3B8',
                        font: { family: 'Plus Jakarta Sans', size: 12 },
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15,30,51,0.95)',
                    borderColor: 'rgba(101,220,213,0.3)',
                    borderWidth: 1,
                    titleColor: '#F1F5F9',
                    bodyColor: '#94A3B8',
                    padding: 12
                }
            }
        }
    });
}
