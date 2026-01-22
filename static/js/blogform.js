console.log("BLOG JS LOADED");

document.addEventListener("DOMContentLoaded", function () {

    const titleInput = document.querySelector('[name="title"]');
    const slugInput  = document.querySelector('[name="slug"]');
    const warning    = document.getElementById("slug-warning");
    const blogIdEl   = document.getElementById("blog-id");

    if (!titleInput || !slugInput) return;

    const blogId = blogIdEl ? blogIdEl.value : "";

    let manualEdit = false;

    function slugify(text) {
        return text
            .toLowerCase()
            .trim()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "");
    }

    
    function checkSlug(slug) {
        if (!slug || !warning) return;

        let url = `/blog/check-slug/?slug=${encodeURIComponent(slug)}`;
        if (blogId) {
            url += `&id=${blogId}`;
        }

        fetch(url)
            .then(res => res.json())
            .then(data => {
                warning.style.display = data.exists ? "inline" : "none";
            })
            .catch(err => {
                console.error("Slug check failed:", err);
                warning.style.display = "none";
            });
    }

    titleInput.addEventListener("input", function () {
        if (manualEdit) return;

        const slug = slugify(this.value);
        slugInput.value = slug;
        checkSlug(slug);
    });

    slugInput.addEventListener("input", function () {
        manualEdit = true;
        checkSlug(this.value);
    });

});



document.addEventListener("DOMContentLoaded", function () {

    const collapseEl = document.getElementById("metadata-section");
    const button = document.querySelector('[data-bs-target="#metadata-section"]');

    let icon = null; // ✅ declare in outer scope

    if (button) {
        icon = button.querySelector("i");
    }

    const metadataOpened = document.getElementById("metadata_opened");

    const titleInput = document.getElementById("id_meta_title");
    const keywordsInput = document.getElementById("id_meta_keywords");
    const descriptionInput = document.getElementById("id_meta_description");

    const titleLeft = document.getElementById("title-left");
    const keywordsLeft = document.getElementById("keywords-left");
    const descriptionLeft = document.getElementById("description-left");

    if (!collapseEl || !titleInput || !keywordsInput || !descriptionInput) return;

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
        updateCounters();
    });

    collapseEl.addEventListener("hidden.bs.collapse", function () {
        metadataOpened.value = "0";
        titleInput.required = false;
        keywordsInput.required = false;
        descriptionInput.required = false;
    });

    collapseEl.addEventListener("show.bs.collapse", function () {
        if (icon) {
            icon.classList.replace("bi-chevron-down", "bi-chevron-up");
        }
    });

    collapseEl.addEventListener("hide.bs.collapse", function () {
        if (icon) {
            icon.classList.replace("bi-chevron-up", "bi-chevron-down");
        }
    });

});
