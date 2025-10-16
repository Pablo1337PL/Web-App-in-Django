function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            const [k, v] = cookie.trim().split('=');
            if (k === name) cookieValue = decodeURIComponent(v);
        });
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
let currentCourses = [];
let sortOrder = { column: null, asc: true };

async function fetchCourses() {
    const q = document.getElementById('q')?.value || '';
    const levelFilter = document.getElementById('levelFilter')?.value || '';

    // Get all checked language checkboxes
    const checkedLanguages = Array.from(document.querySelectorAll('.language-checkbox:checked'))
        .map(cb => cb.value);

    let url = `/courses/?q=${encodeURIComponent(q)}`;

    // Add level filter
    if (levelFilter) {
        url += `&level=${encodeURIComponent(levelFilter)}`;
    }

    // Add each selected language as a separate parameter
    checkedLanguages.forEach(langId => {
        url += `&language=${encodeURIComponent(langId)}`;
    });

    const rsp = await fetch(url, {
        headers: { 'x-requested-with': 'XMLHttpRequest' },
        method: 'GET',
    });

    if (!rsp.ok) return;

    const data = await rsp.json();
    currentCourses = data.courses;
    renderCourses(currentCourses);
}

function renderCourses(courses) {
    const tbody = document.querySelector('#coursesTable tbody');
    tbody.innerHTML = '';

    if (courses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No courses found.</td></tr>';
        return;
    }

    courses.forEach(c => {
        const tr = document.createElement('tr');

        // Build programming languages display
        let languagesHTML = '<span class="text-muted">None</span>';
        if (c.programming_languages && c.programming_languages.length > 0) {
            languagesHTML = c.programming_languages.map(lang =>
                `<span class="badge bg-primary text-white me-1">${lang.name}</span>`
            ).join(' ');
        }

        // Build level display with colored badge
        let levelBadgeClass = 'bg-secondary';
        switch(c.level) {
            case 1: levelBadgeClass = 'bg-success'; break;
            case 2: levelBadgeClass = 'bg-info'; break;
            case 3: levelBadgeClass = 'bg-warning text-dark'; break;
            case 4: levelBadgeClass = 'bg-purple text-white'; break;
            case 5: levelBadgeClass = 'bg-danger'; break;
        }
        const levelHTML = `<span class="badge ${levelBadgeClass}">${c.level_display}</span>`;

        // Build actions column
        let actionsHTML = '';
        if (c.is_staff) {
            actionsHTML = `
                <a href="/staff/courses/edit/${c.id}/" class="btn btn-sm btn-warning">Edit</a>
                <form action="/staff/courses/delete/${c.id}/" method="post" style="display:inline;">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                    <button type="submit" class="btn btn-sm btn-danger">Delete</button>
                </form>
            `;
        }

        tr.innerHTML = `
            <td>${c.name}</td>
            <td>${c.description}</td>
            <td>${levelHTML}</td>
            <td>${languagesHTML}</td>
            <td>${actionsHTML}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Filter courses as you type
const qInput = document.getElementById('q');
if (qInput) {
    qInput.addEventListener('input', () => {
        fetchCourses();
    });
}

// Filter by language checkboxes
document.querySelectorAll('.language-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', () => {
        fetchCourses();
    });
});

// Filter by level
const levelFilterElement = document.getElementById('levelFilter');
if (levelFilterElement) {
    levelFilterElement.addEventListener('change', () => {
        fetchCourses();
    });
}

// Sorting
document.querySelectorAll('#coursesTable th.sortable').forEach(th => {
    th.addEventListener('click', () => {
        const col = th.dataset.column;
        if (sortOrder.column === col) sortOrder.asc = !sortOrder.asc;
        else sortOrder = { column: col, asc: true };

        currentCourses.sort((a, b) => {
            let valA = a[col];
            let valB = b[col];

            if (Array.isArray(valA)) valA = valA.join(', ');
            if (Array.isArray(valB)) valB = valB.join(', ');

            if (valA < valB) return sortOrder.asc ? -1 : 1;
            if (valA > valB) return sortOrder.asc ? 1 : -1;
            return 0;
        });

        renderCourses(currentCourses);
    });
});
