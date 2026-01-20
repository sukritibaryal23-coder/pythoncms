$(document).ready(function() {
    // 1. Get CSRF Token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // 2. Initialize DataTable
    // We disable pagination and ordering so SortableJS has full control
    const table = $('#listTable').DataTable({
        paging: true,
        ordering: false,
        pageLength: 10,
        columnDefs: [
            { targets: 0, visible: false } // Hide the ID/Position column
        ]
    });



    // 3. Initialize SortableJS on the tbody
    const el = document.querySelector('#listTable tbody');
    const sortUrl = $('#listTable').data('sort-url');
    Sortable.create(el, {
        handle: '.drag-handle', // <--- This restricts drag to the handle
        animation: 200,         // Smooth sliding animation (ms)
        ghostClass: 'sortable-ghost',
        onEnd: function () {
            let newOrder = [];
            
            // Loop through all rows in current DOM order to get their data-ids
            $('#listTable tbody tr').each(function() {
                const id = $(this).data('id');
                if(id) newOrder.push(id);
            });

            // 4. Send the new ID list to the server
            $.ajax({
                url: sortUrl,
                method: "POST",
                headers: { "X-CSRFToken": csrftoken },
                contentType: "application/json",
                data: JSON.stringify({ order: newOrder }),
                success: function() {
                    const box = document.getElementById("action-message");
                    if (box) {
                        box.innerHTML = `<div class="alert alert-success" role="alert">Sorted Successfully!</div>`;
                        setTimeout(() => { box.innerHTML = ""; }, 2000);
                    }
                },
                error: function() {
                    alert('Save failed. Please refresh and try again.');
                }
            });
        }
    });
});
document.addEventListener("DOMContentLoaded", function () {
    // CSRF helper
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            document.cookie.split(";").forEach(cookie => {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                }
            });
        }
        return cookieValue;
    }
    const csrftoken = getCookie("csrftoken");

    // Show status-style message
    function showStatusMessage(text, type = "success") {
        const box = document.getElementById("action-message");
        if (!box) return;

        box.innerHTML = `<div class="alert alert-${type}" role="alert">${text}</div>`;
        setTimeout(() => { box.innerHTML = ""; }, 2000);
    }

    // Delete button click
    document.querySelectorAll(".delete-blog-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const blogId = this.dataset.id;

            // Confirmation
            if (!confirm("Do you want to delete the blog?")) return;

            fetch(`/blog/delete/${blogId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest",
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Remove the row
                    this.closest("tr").remove();

                    // Show success message
                    showStatusMessage(data.message || "Blog deleted successfully", "success");
                } else {
                    // Show error message
                    showStatusMessage(data.message || "Delete failed", "danger");
                }
            })
            .catch(err => {
                console.error(err);
                showStatusMessage("AJAX request failed", "danger");
            });
        });
    });
});

// Toggle publish status

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("click", function (e) {
    const btn = e.target.closest(".toggle-status-btn");
    if (!btn) return;

    const blogId = btn.dataset.id;

    fetch(`/blog/toggle-status/${blogId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            if (data.active) {
                btn.classList.remove("btn-secondary");
                btn.classList.add("btn-success");
                btn.textContent = "Published";
            } else {
                btn.classList.remove("btn-success");
                btn.classList.add("btn-secondary");
                btn.textContent = "Unpublished";
            }
            showStatusMessage(data.message || "Status updated.", "success");
        } else {
            showStatusMessage(data.message || "Failed to update status.", "danger");
        }
    })
    .catch(err => {
        console.error(err);
        showStatusMessage("AJAX request failed.", "danger");
    });
});

function showStatusMessage(text, type = "success") {
    const box = document.getElementById("status-toggle-message");
    if (!box) return;
    box.innerHTML = `<div class="alert alert-${type}" role="alert">${text}</div>`;
    setTimeout(() => { box.innerHTML = ""; }, 2000);
}
