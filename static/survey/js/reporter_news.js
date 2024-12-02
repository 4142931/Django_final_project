document.getElementById('applyFilters').addEventListener('click', function () {
    const date = document.getElementById('dateFilter').value;
    const reporter = document.getElementById('reporterFilter').value;
    const keyword = document.getElementById('keywordFilter').value;
    const rating = document.getElementById('ratingFilter').value;

    const rows = document.querySelectorAll('#newsTable tbody tr');
    rows.forEach(row => {
        const dateCell = row.cells[2].textContent;
        const reporterCell = row.cells[1].textContent;
        const titleCell = row.cells[0].textContent;
        const ratingCell = row.cells[3].dataset.rating;

        const matchesDate = !date || dateCell.startsWith(date);
        const matchesReporter = !reporter || reporterCell.toLowerCase().includes(reporter.toLowerCase());
        const matchesKeyword = !keyword || titleCell.toLowerCase().includes(keyword.toLowerCase());
        const matchesRating = !rating || ratingCell === rating;

        row.style.display = matchesDate && matchesReporter && matchesKeyword && matchesRating ? '' : 'none';
    });
});
