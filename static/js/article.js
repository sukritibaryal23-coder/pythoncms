//-------------//
//ARTICLE LIST//
//-------------//

// <!-- draggable sorting -->

document.addEventListener('DOMContentLoaded', function() {
    const tbody = document.getElementById('article-table-body');

    if (!tbody) return; // safety check

    new Sortable(tbody, {
        handle: '.drag-handle',       // only drag using the ☰
        animation: 150,               // smooth animation
        ghostClass: 'dragging',       // optional class while dragging
        dataIdAttr: 'data-id',        // use data-id for tracking
        direction: 'vertical',        // vertical movement
        tag: 'tr',                    // important for table rows
        onEnd: function(evt) {
            // get the new order of article IDs
            const order = Array.from(tbody.children).map(tr => tr.dataset.id);
            console.log("New order:", order);

            // send the new order to Django backend
            fetch("{% url 'article_reorder' %}", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": "{{ csrf_token }}"
                },
                body: JSON.stringify({ order: order })
            })
            .then(response => response.json())
            .then(data => console.log("Server response:", data))
            .catch(error => console.error("Error saving order:", error));
        }
    });
});

// <!-- search -->

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("article-search-form");
    const input = document.getElementById("article-search");
    const tableBody = document.getElementById("article-table-body");

    let typingTimer = null;

    function doSearch() {
        const query = input.value.trim();
        const params = new URLSearchParams(window.location.search);

        // preserve homepage & per_page filters
        const homepage = params.get("homepage") || "1";
        const per_page = params.get("per_page") || "10";

        params.set("homepage", homepage);
        params.set("per_page", per_page);
        params.delete("page"); // reset to page 1

        if (query === "") {
            params.delete("q");
        } else {
            params.set("q", query);
        }

        fetch(`/articles/?${params.toString()}`, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
        .then(res => res.json())
        .then(data => {
            tableBody.innerHTML = data.html;
            history.replaceState(null, "", `/articles/?${params.toString()}`);
        })
        .catch(err => console.error(err));
    }

    // Submit search (enter / button)
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        doSearch();
    });

    // Live search as user types (debounced)
    input.addEventListener("input", function () {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(doSearch, 100); // 300ms debounce
    });
});


// <!-- checkbox -->

    // Select/Deselect all checkboxes
    document.getElementById('select-all').addEventListener('click', function(){
        let checkboxes = document.querySelectorAll('input[name="selected_articles"]');
        checkboxes.forEach(cb => cb.checked = this.checked);
    });


// <!-- homepage filter -->

function applyFilter() {
    const filter = document.getElementById("homepage-filter").value;
    const params = new URLSearchParams(window.location.search);

    if (filter === "") {
        params.delete("homepage");
    } else {
        params.set("homepage", filter);
    }

    window.location.search = params.toString();
}


// <!-- Toggle status -->

document.addEventListener("click", function (e) {
    if (!e.target.classList.contains("toggle-status-btn")) return;

    const btn = e.target;
    const articleId = btn.dataset.id;

    fetch(`/articles/toggle-status/${articleId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            if (data.status) {
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
    });
});

function showStatusMessage(text, type = "success") {
    const box = document.getElementById("status-toggle-message");
    if (!box) return;

    box.innerHTML = `
        <div class="alert alert-${type} mt-2 mb-0" role="alert">
            ${text}
        </div>
    `;
    setTimeout(() => {
        box.innerHTML = "";
    }, 2000);
}

function getCookie(name) {
    let cookieValue = null;
    document.cookie.split(";").forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
            cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
        }
    });
    return cookieValue;
}

// <!-- delete -->

document.addEventListener("DOMContentLoaded", function () {
    const tableBody = document.getElementById("article-table-body");
    const messageBox = document.getElementById("action-message");

    tableBody.addEventListener("click", function (e) {
        const btn = e.target.closest(".delete-article-btn");
        if (!btn) return;

        const articleId = btn.dataset.id;
        if (!confirm("Are you sure you want to delete this article?")) return;

        const params = new URLSearchParams(window.location.search);

        fetch(`/articles/delete/${articleId}/?${params.toString()}`, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                btn.closest("tr").remove();
                showMessage(data.message || "Deleted successfully.", "success");
            } else {
                showMessage(data.message || "Failed to delete article.", "danger");
            }
        })
        .catch(() => {
            showMessage("An error occurred.", "danger");
        });
    });

    function showMessage(text, type) {
        if (!messageBox) return;
        messageBox.innerHTML = `
            <div class="alert alert-${type} mt-2">
                ${text}
            </div>`;
        setTimeout(() => {
            messageBox.innerHTML = "";
        }, 2000);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});


// <!-- bulk actions -->
 
document.addEventListener("DOMContentLoaded", function () {
    const tableBody = document.getElementById("article-table-body");

    // Bulk action buttons
    const bulkButtons = document.querySelectorAll(".bulk-action-btn");

    bulkButtons.forEach(btn => {
        btn.addEventListener("click", function () {
            const action = btn.dataset.action;

            // Get selected article IDs
            const selected = [...document.querySelectorAll("input[name='selected_articles']:checked")]
                .map(cb => cb.value);

            if (!selected.length) {
                showBulkMessage("Please select at least one article.", "warning");
                return;
            }
            if (action === "delete" && !confirm("Are you sure you want to delete selected articles?")) return;

            const formData = new FormData();
            formData.append("action", action);
            selected.forEach(id => formData.append("selected_articles[]", id));

            fetch("{% url 'article_bulk_action' %}", {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (action === "delete") {
                        // Remove deleted rows
                        selected.forEach(id => {
                            const row = document.querySelector(`tr[data-id='${id}']`);
                            if (row) row.remove();
                        });
                    } else if (action === "publish") {
                        // Toggle status buttons in table
                        selected.forEach(id => {
                            const tbtn = document.querySelector(`tr[data-id='${id}'] .toggle-status-btn`);
                            if (tbtn) {
                                tbtn.classList.toggle("btn-success");
                                tbtn.classList.toggle("btn-secondary");
                                tbtn.textContent =
                                    tbtn.textContent === "Published" ? "Unpublished" : "Published";
                            }
                        });
                    }

                    showBulkMessage(data.message || "Action completed.", "success");
                } else {
                    showBulkMessage(data.message || "Action failed.", "danger");
                }
            });
        });
    });

    function showBulkMessage(text, type = "success") {
        const box = document.getElementById("bulk-action-message");
        if (!box) return;

        box.innerHTML = `
            <div class="alert alert-${type} mt-2 mb-0" role="alert">
                ${text}
            </div>
        `;

        setTimeout(() => {
            box.innerHTML = "";
        }, 2000);
    }

    // Helper to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});


//-------------//
//ARTICLE FORM//
//-------------//

//slug
    // References
    const titleInput = document.getElementById("id_title");
    const slugInput = document.getElementById("id_slug");
    const warning = document.getElementById("slug-warning");

    // Get current article ID if editing, empty for Add
    const articleId = "{{ form.instance.pk|default:'' }}";

    // AUTO-GENERATE SLUG FROM TITLE
    titleInput.addEventListener("input", function() {
        let slug = this.value
            .toLowerCase()
            .trim()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '');
        slugInput.value = slug;

        // Immediately check slug after generating
        checkSlug(slug);
    });

    // CHECK SLUG WHEN TYPING MANUALLY
    slugInput.addEventListener("input", function() {
        checkSlug(this.value);
    });

    function checkSlug(slug) {
        if (!slug) {
            warning.style.display = "none";
            return;
        }

        // Include article ID for edit page
        let url = `/articles/check-slug/?slug=${slug}`;
        if (articleId) {
            url += `&id=${articleId}`;
        }

        fetch(url)
            .then(response => response.json())
            .then(data => {
                warning.style.display = data.exists ? "block" : "none";
            });
    }

    // LIVE IMAGE PREVIEW
    const fileInput = document.getElementById('id_image');
    const preview = document.getElementById('preview');

    fileInput.addEventListener('change', function(event){
        const [file] = fileInput.files;
        if(file){
            preview.src = URL.createObjectURL(file); // display selected image
            preview.style.display = 'block';         // make visible
        } else {
            preview.src = "";
            preview.style.display = 'none';
        }
    });


//remove image
document.addEventListener("DOMContentLoaded", function() {
    const removeBtn = document.getElementById("remove-image-btn");
    const preview = document.getElementById("preview");
    const fileInputContainer = document.getElementById("file-input-container");
    const imagePath = document.getElementById("image-path");
    const fileInput = fileInputContainer.querySelector("input[type=file]");
    const deleteFlag = document.getElementById("delete-image-flag"); // 🔹 define the hidden input

    if (removeBtn) {
        removeBtn.addEventListener("click", function () {
            // Hide preview and remove button
            preview.style.display = "none";
            removeBtn.style.display = "none";

            // Show file input again
            fileInputContainer.style.display = "block";

            // Clear file input and image path
            if (fileInput) fileInput.value = "";
            imagePath.textContent = "";

            // 🔴 Set delete flag to 1 so Django deletes the image
            if (deleteFlag) deleteFlag.value = "1";
        });
    }

    // Live preview for newly selected file
    if (fileInput) {
        fileInput.addEventListener("change", function() {
            const file = this.files[0];
            if (file) {
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = "block";
                    removeBtn.style.display = "flex";
                    fileInputContainer.style.display = "none";
                    imagePath.textContent = file.name;

                    // 🔹 Reset delete flag if a new file is chosen
                    if (deleteFlag) deleteFlag.value = "0";
                }
                reader.readAsDataURL(file);
            }
        });
    }
});

//metadata dropdown
document.addEventListener('DOMContentLoaded', function() {
    const collapseEl = document.getElementById('metadata-section');
    const button = collapseEl.previousElementSibling; // the button
    const icon = button.querySelector('i');

    collapseEl.addEventListener('show.bs.collapse', function () {
        icon.classList.remove('bi-chevron-down');
        icon.classList.add('bi-chevron-up');
    });

    collapseEl.addEventListener('hide.bs.collapse', function () {
        icon.classList.remove('bi-chevron-up');
        icon.classList.add('bi-chevron-down');
    });
});


//metadata restrictions
document.addEventListener("DOMContentLoaded", function () {

    const metadataSection = document.getElementById("metadata-section");
    const metadataOpened = document.getElementById("metadata_opened");

    const titleInput = document.getElementById("meta_title");
    const keywordsInput = document.getElementById("meta_keywords");
    const descriptionInput = document.getElementById("meta_description");

    const titleLeft = document.getElementById("title-left");
    const keywordsLeft = document.getElementById("keywords-left");
    const descriptionLeft = document.getElementById("description-left");

    function updateTitle() {
        titleLeft.textContent = 60 - titleInput.value.length;
    }

    function updateKeywords() {
        keywordsLeft.textContent = 250 - keywordsInput.value.length;
    }

    function updateDescription() {
        descriptionLeft.textContent = 160 - descriptionInput.value.length;
    }

    // Initial update (edit form case)
    updateTitle();
    updateKeywords();
    updateDescription();

    titleInput.addEventListener("input", updateTitle);
    keywordsInput.addEventListener("input", updateKeywords);
    descriptionInput.addEventListener("input", updateDescription);

    // 🔥 Toggle required based on dropdown
    metadataSection.addEventListener("shown.bs.collapse", function () {
        metadataOpened.value = "1";
        titleInput.required = true;
        keywordsInput.required = true;
        descriptionInput.required = true;
    });

    metadataSection.addEventListener("hidden.bs.collapse", function () {
        metadataOpened.value = "0";
        titleInput.required = false;
        keywordsInput.required = false;
        descriptionInput.required = false;
    });
});

window.addEventListener("load", function () {
    const button = document.getElementById("readmore-btn");
    if (!button || !window.CKEDITOR) return;

    const instanceName = Object.keys(CKEDITOR.instances)[0];
    const editor = CKEDITOR.instances[instanceName];
    if (!editor) return;

    editor.on("instanceReady", function () {
        button.addEventListener("click", function () {

            // ✅ Permanent check
            if (editor.getData().includes('class="read-more"')) {
                alert("Only one Read More line is allowed.");
                return;
            }

            editor.insertHtml(
                '<hr class="read-more" style="border: 2px dashed orange;" />'
            );
        });
    });
});

