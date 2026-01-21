

//slug

document.addEventListener("DOMContentLoaded", function () {

    const titleInput = document.getElementById("id_title");
    const slugInput = document.getElementById("id_slug");

    if (!titleInput || !slugInput) {
        console.log("Slug inputs not found");
        return;
    }

    titleInput.addEventListener("input", function () {
        const slug = this.value
            .toLowerCase()
            .trim()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "");

        slugInput.value = slug;
    });

});


document.addEventListener("DOMContentLoaded", function () {

    const titleInput = document.getElementById("id_title");
    const slugInput = document.getElementById("id_slug");
    const warning = document.getElementById("slug-warning");

    // Blog ID for edit page, empty on create
    const blogId = "{{ form.instance.pk|default:'' }}";

    if (!titleInput || !slugInput || !warning) return;

    let manualEdit = false;

    // Auto-generate slug from title
    titleInput.addEventListener("input", function () {
        if (manualEdit) return;

        const slug = this.value
            .toLowerCase()
            .trim()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "");

        slugInput.value = slug;

        checkSlug(slug);
    });

    // Check slug when typing manually
    slugInput.addEventListener("input", function () {
        manualEdit = true;
        checkSlug(this.value);
    });

    function checkSlug(slug) {
        if (!slug) {
            warning.style.display = "none";
            return;
        }

        // Build URL for checking slug
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
                console.error(err);
                warning.style.display = "none";
            });
    }

});
