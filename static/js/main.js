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
let currentProjects = [];
let sortOrder = { column: null, asc: true };

async function fetchProjects() {
    const q = document.getElementById('q')?.value || '';

    // Get all checked category checkboxes
    const checkedCategories = Array.from(document.querySelectorAll('.category-checkbox:checked'))
        .map(cb => cb.value);

    let url = `/projects/?q=${encodeURIComponent(q)}`;

    // Add each selected category as a separate parameter
    checkedCategories.forEach(catId => {
        url += `&category=${encodeURIComponent(catId)}`;
    });

    const rsp = await fetch(url, {
        headers: { 'x-requested-with': 'XMLHttpRequest' },
        method: 'GET',
    });

    if (!rsp.ok) return;

    const data = await rsp.json();
    currentProjects = data.projects;
    renderProjects(currentProjects);
}

function renderProjects(projects) {
    const tbody = document.querySelector('#projectsTable tbody');
    tbody.innerHTML = '';

    if (projects.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">No projects found.</td></tr>';
        return;
    }

    projects.forEach(p => {
        const tr = document.createElement('tr');

        // Build participants display
        let participantsHTML = '';
        if (p.participants && p.participants.length > 0) {
            participantsHTML = p.participants.map(u => {
                if (p.is_staff) {
                    return `${u.username} <button class="btn btn-xs btn-outline-danger remove-btn" data-id="${u.assignment_id}" title="Remove">×</button>`;
                }
                return u.username;
            }).join(', ');
        } else {
            participantsHTML = '<span class="text-muted">None</span>';
        }

        // If staff, show pending applications with accept/reject buttons
        if (p.is_staff && p.pending_applications && p.pending_applications.length > 0) {
            const pendingHTML = p.pending_applications.map(app =>
                `${app.username}
                <button class="btn btn-xs btn-success accept-btn" data-id="${app.application_id}" title="Accept">✓</button>
                <button class="btn btn-xs btn-danger reject-btn" data-id="${app.application_id}" title="Reject">✗</button>`
            ).join(', ');
            participantsHTML += `<br><strong>Pending:</strong> ${pendingHTML}`;
        }

        // Build actions column
        let actionsHTML = '';

        if (p.can_apply) {
            actionsHTML += `<button class="btn btn-sm btn-success apply-btn" data-id="${p.id}">Apply</button>`;
        } else if (p.user_status === 'pending') {
            actionsHTML += `<span class="badge bg-warning">Application Pending</span>`;
        } else if (p.user_status === 'accepted') {
            actionsHTML += `<span class="badge bg-success">Accepted</span>`;
        }

        if (p.is_admin) {
            actionsHTML += `
                <a href="/staff/projects/edit/${p.id}/" class="btn btn-sm btn-warning">Edit</a>
                <form action="/staff/projects/delete/${p.id}/" method="post" style="display:inline;">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Delete this project?')">Delete</button>
                </form>
            `;
        }

        // Build categories display
        let categoriesHTML = '<span class="text-muted">None</span>';
        if (p.categories && p.categories.length > 0) {
            categoriesHTML = p.categories.map(c => `<span class="badge bg-info text-dark me-1">${c.name}</span>`).join(' ');
        }

        // Build mentors display
        let mentorsHTML = '<span class="text-muted">None</span>';
        if (p.mentors && p.mentors.length > 0) {
            mentorsHTML = p.mentors.map(m => `<span class="badge bg-success me-1">${m.username}</span>`).join(' ');
        }

        // Add mentor/unmentor button for staff
        if (p.is_staff) {
            if (p.is_mentoring) {
                actionsHTML = `<button class="btn btn-sm btn-outline-danger unmentor-btn" data-id="${p.id}">Stop Mentoring</button>` + actionsHTML;
            } else {
                actionsHTML = `<button class="btn btn-sm btn-outline-success mentor-btn" data-id="${p.id}">Become Mentor</button>` + actionsHTML;
            }
        }

        tr.innerHTML = `
            <td>${p.name}</td>
            <td>${p.description}</td>
            <td>${categoriesHTML}</td>
            <td>${mentorsHTML}</td>
            <td>${participantsHTML}</td>
            <td>${actionsHTML}</td>
        `;
        tbody.appendChild(tr);
    });

    // Add event listeners to apply buttons
    document.querySelectorAll('.apply-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const projectId = btn.dataset.id;
            const applyResp = await fetch(`/projects/apply/${projectId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'x-requested-with': 'XMLHttpRequest',
                },
            });

            const result = await applyResp.json();
            if (result.success) {
                alert('Application submitted successfully!');
                fetchProjects();
            } else {
                alert(result.message || 'Failed to apply');
            }
        });
    });

    // Add event listeners to accept buttons (staff only)
    document.querySelectorAll('.accept-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const applicationId = btn.dataset.id;
            const acceptResp = await fetch(`/projects/accept/${applicationId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'x-requested-with': 'XMLHttpRequest',
                },
            });

            const result = await acceptResp.json();
            if (result.success) {
                fetchProjects();
            } else {
                alert(result.message || 'Failed to accept application');
            }
        });
    });

    // Add event listeners to reject buttons (staff only)
    document.querySelectorAll('.reject-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const applicationId = btn.dataset.id;
            if (confirm('Reject this application?')) {
                const rejectResp = await fetch(`/projects/reject/${applicationId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'x-requested-with': 'XMLHttpRequest',
                    },
                });

                const result = await rejectResp.json();
                if (result.success) {
                    fetchProjects();
                } else {
                    alert(result.message || 'Failed to reject application');
                }
            }
        });
    });

    // Add event listeners to remove buttons (staff only)
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const assignmentId = btn.dataset.id;
            if (confirm('Remove this user from the project?')) {
                const removeResp = await fetch(`/projects/remove/${assignmentId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'x-requested-with': 'XMLHttpRequest',
                    },
                });

                const result = await removeResp.json();
                if (result.success) {
                    fetchProjects();
                } else {
                    alert(result.message || 'Failed to remove user');
                }
            }
        });
    });

    // Add event listeners to mentor buttons (staff only)
    document.querySelectorAll('.mentor-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const projectId = btn.dataset.id;
            const mentorResp = await fetch(`/projects/mentor/${projectId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'x-requested-with': 'XMLHttpRequest',
                },
            });

            const result = await mentorResp.json();
            if (result.success) {
                fetchProjects();
            } else {
                alert(result.message || 'Failed to become mentor');
            }
        });
    });

    // Add event listeners to unmentor buttons (staff only)
    document.querySelectorAll('.unmentor-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const projectId = btn.dataset.id;
            const unmentorResp = await fetch(`/projects/unmentor/${projectId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'x-requested-with': 'XMLHttpRequest',
                },
            });

            const result = await unmentorResp.json();
            if (result.success) {
                fetchProjects();
            } else {
                alert(result.message || 'Failed to stop mentoring');
            }
        });
    });
}

// Filter projects as you type
const qInput = document.getElementById('q');
if (qInput) {
    qInput.addEventListener('input', () => {
        fetchProjects();
    });
}

// Filter by category checkboxes
document.querySelectorAll('.category-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', () => {
        fetchProjects();
    });
});

// Sorting
document.querySelectorAll('#projectsTable th.sortable').forEach(th => {
    th.addEventListener('click', () => {
        const col = th.dataset.column;
        if (sortOrder.column === col) sortOrder.asc = !sortOrder.asc;
        else sortOrder = { column: col, asc: true };

        currentProjects.sort((a, b) => {
            let valA = a[col];
            let valB = b[col];

            if (Array.isArray(valA)) valA = valA.join(', ');
            if (Array.isArray(valB)) valB = valB.join(', ');

            if (valA < valB) return sortOrder.asc ? -1 : 1;
            if (valA > valB) return sortOrder.asc ? 1 : -1;
            return 0;
        });

        renderProjects(currentProjects);
    });
});
