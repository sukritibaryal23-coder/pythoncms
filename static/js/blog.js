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

// Select/Deselect all checkboxes
    document.getElementById('select-all').addEventListener('click', function(){
        let checkboxes = document.querySelectorAll('input[name="selected_blogs"]');
        checkboxes.forEach(cb => cb.checked = this.checked);
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

//bulk action

document.addEventListener("DOMContentLoaded", function() {
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

    function performBulkAction(action) {
        const selected = Array.from(document.querySelectorAll('input[name="selected_blogs"]:checked'))
                              .map(cb => cb.value);
        if (!selected.length) {
            alert("No blogs selected.");
            return;
        }

        if (action === "delete" && !confirm("Do you want to delete the selected blogs?")) return;

        const formData = new FormData();
        formData.append("action", action);
        selected.forEach(id => formData.append("selected_blogs[]", id));

        fetch(`/blog/bulk-action/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // If delete, remove rows
                if (action === "delete") {
                    selected.forEach(id => {
                        const row = document.querySelector(`#listTable tbody tr[data-id="${id}"]`);
                        if (row) row.remove();
                    });
                }
                // If publish, toggle button text and color
                if (action === "publish") {
                    selected.forEach(id => {
                        const btn = document.querySelector(`tr[data-id="${id}"] .toggle-status-btn`);
                        if (btn) {
                            btn.classList.toggle("btn-success");
                            btn.classList.toggle("btn-secondary");
                            btn.textContent = btn.classList.contains("btn-success") ? "Published" : "Unpublished";
                        }
                    });
                }

                // Show success message
                const box = document.getElementById("action-message");
                if (box) {
                    box.innerHTML = `<div class="alert alert-success" role="alert">${data.message}</div>`;
                    setTimeout(() => { box.innerHTML = ""; }, 2000);
                }
            } else {
                alert(data.message || "Bulk action failed.");
            }
        })
        .catch(err => console.error(err));
    }

    document.getElementById("bulk-publish").addEventListener("click", () => performBulkAction("publish"));
    document.getElementById("bulk-delete").addEventListener("click", () => performBulkAction("delete"));
});


document.addEventListener("DOMContentLoaded", function () {

    const collapseEl = document.getElementById("metadata-section");
    const button = document.querySelector('[data-bs-target="#metadata-section"]');
    const icon = button.querySelector("i");

    const metadataOpened = document.getElementById("metadata_opened");

    const titleInput = document.getElementById("id_meta_title");
    const keywordsInput = document.getElementById("id_meta_keywords");
    const descriptionInput = document.getElementById("id_meta_description");

    const titleLeft = document.getElementById("title-left");
    const keywordsLeft = document.getElementById("keywords-left");
    const descriptionLeft = document.getElementById("description-left");

    if (!titleInput || !keywordsInput || !descriptionInput) return;

    function updateCounters() {
        titleLeft.textContent = 60 - titleInput.value.length;
        keywordsLeft.textContent = 250 - keywordsInput.value.length;
        descriptionLeft.textContent = 160 - descriptionInput.value.length;
    }

    titleInput.addEventListener("input", updateCounters);
    keywordsInput.addEventListener("input", updateCounters);
    descriptionInput.addEventListener("input", updateCounters);

    collapseEl.addEventListener("shown.bs.collapse", function () {
        metadataOpened.value = "1";
        titleInput.required = true;
        keywordsInput.required = true;
        descriptionInput.required = true;
        updateCounters(); // 🔥 critical
    });

    collapseEl.addEventListener("hidden.bs.collapse", function () {
        metadataOpened.value = "0";
        titleInput.required = false;
        keywordsInput.required = false;
        descriptionInput.required = false;
    });

    collapseEl.addEventListener("show.bs.collapse", function () {
        icon.classList.replace("bi-chevron-down", "bi-chevron-up");
    });

    collapseEl.addEventListener("hide.bs.collapse", function () {
        icon.classList.replace("bi-chevron-up", "bi-chevron-down");
    });

});





