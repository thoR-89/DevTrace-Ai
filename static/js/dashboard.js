document.addEventListener('DOMContentLoaded', function() {
    fetchAdminStats();
});

function fetchAdminStats() {
    fetch('/api/admin/stats')
        .then(response => response.json())
        .then(data => {
            if (data.platforms) {
                renderPlatformChart(data.platforms);
            }
        })
        .catch(err => console.error('Admin Stats Error:', err));
}

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
                    '#2563EB',
                    '#0A66C2',
                    '#FFA116',
                    '#2EC4B6'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#CBD5E1', font: { family: 'Plus Jakarta Sans' } }
                }
            }
        }
    });
}
