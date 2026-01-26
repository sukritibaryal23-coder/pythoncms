$(document).ready(function() {

    function getCsrfToken() {
        return document.cookie.match(/csrftoken=([^;]+)/)?.[1];
    }

    // Upload
    $('#upload-btn').click(() => $('#file-upload').click());
    $('#file-upload').on('change', function () {
        const formData = new FormData();
        for (let file of this.files) formData.append('file', file);
        formData.append('folder', "{{ current_folder.id|default:'' }}");
        formData.append('csrfmiddlewaretoken', getCsrfToken());

        $.ajax({
            url: "{% url 'contentmgmt:upload_file' %}",
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: () => location.reload()
        });
    });

    // Create folder
    $('#create-folder-btn').click(() => {
        const name = prompt("Folder name");
        if (!name) return;

        $.post("{% url 'contentmgmt:create_folder' %}", {
            name: name,
            parent: "{{ current_folder.id|default:'' }}",
            csrfmiddlewaretoken: getCsrfToken()
        }).done(() => location.reload());
    });

    // Double-click folder / file
    $('.explorer-card, .explorer-item').on('dblclick', function() {
        const type = $(this).data('type');
        const id = $(this).data('id');
        const fileName = $(this).find('.editable-name').text().trim();
        const fileId = $(this).data('id');

        $('#preview-filename')
            .text(fileName)
            .attr('data-id', fileId);


        if (type === 'folder') {
            window.location.href = "{% url 'contentmgmt:folder_view' 0 %}".replace('/0/', '/' + id + '/');
        } else if (type === 'file') {
            const $img = $(this).find('img');
            const $video = $(this).find('video');

            if ($img.length) {
                $('#preview-image').attr('src', $img.attr('src')).removeClass('d-none');
                $('#preview-video').addClass('d-none');
            } else if ($video.length) {
                $('#preview-video').attr('src', $video.attr('src')).removeClass('d-none');
                $('#preview-image').addClass('d-none');
            }

            $('#download-preview').attr('href', $(this).find('a').attr('href'));
            const myModal = new bootstrap.Modal(document.getElementById('previewModal'));
            myModal.show();
        }
    });

    // Delete without reload
    $(document).on('click', '.delete-item', function(e) {
        e.stopPropagation();
        if (!confirm("Delete this item?")) return;

        const $btn = $(this);
        const $card = $btn.closest('[data-id]');
        const id = $btn.data('id');
        const type = $btn.data('type');

        $.post("{% url 'contentmgmt:delete_item' %}", {
            id: id,
            type: type,
            csrfmiddlewaretoken: getCsrfToken()
        }).done(res => {
            if (res.success) {
                $card.fadeOut(200, function() { $(this).remove(); });
            }
        });
    });

    // Toggle status
    $(document).on('click', '.toggle-status', function(e) {
        e.stopPropagation();
        const $btn = $(this);
        const id = $btn.data('id');
        const type = $btn.data('type');

        $.post("{% url 'contentmgmt:toggle_status' %}", {
            id: id,
            type: type,
            csrfmiddlewaretoken: getCsrfToken()
        }).done(res => {
            if (res.success) {
                const icon = res.status ? 'on' : 'off';
                $btn.find('i').removeClass('fa-toggle-on fa-toggle-off').addClass('fa-toggle-' + icon);
            }
        });
    });

    // Select all
    $('#select-all').on('change', function() {
        $('.item-checkbox').prop('checked', this.checked);
    });

    // Bulk toggle status
    $('#bulk-toggle-status').on('click', function() {
        const selected = $('.item-checkbox:checked');
        if (!selected.length) return alert("Select items first.");

        selected.each(function() {
            const $card = $(this).closest('[data-id]');
            const id = $card.data('id');
            const type = $card.data('type');

            $.post("{% url 'contentmgmt:toggle_status' %}", {
                id: id,
                type: type,
                csrfmiddlewaretoken: getCsrfToken()
            }).done(res => {
                if (res.success) {
                    const $icon = $card.find('.toggle-status i');
                    const icon = res.status ? 'on' : 'off';
                    $icon.removeClass('fa-toggle-on fa-toggle-off').addClass('fa-toggle-' + icon);
                }
            });
        });
    });

    // Bulk delete
    $('#bulk-delete').on('click', function() {
        const selected = $('.item-checkbox:checked');
        if (!selected.length) return alert("Select items first.");
        if (!confirm("Delete selected items?")) return;

        selected.each(function() {
            const $card = $(this).closest('[data-id]');
            const id = $card.data('id');
            const type = $card.data('type');

            $.post("{% url 'contentmgmt:delete_item' %}", {
                id: id,
                type: type,
                csrfmiddlewaretoken: getCsrfToken()
            }).done(res => { 
                if (res.success) $card.fadeOut(200, function() { $(this).remove(); }); 
            });
        });
    });

});

// Inline rename
$(document).ready(function() {

    function getCsrfToken() {
        return document.cookie.match(/csrftoken=([^;]+)/)?.[1];
    }

    $(document).on('blur keydown', '.editable-name', function(e) {
        const elem = $(this);
        const id = elem.data('id');
        const type = elem.data('type');
        const newName = elem.text().trim();

        if (e.type === 'blur' || (e.type === 'keydown' && e.key === 'Enter')) {
            if (e.type === 'keydown') e.preventDefault();
            elem.blur();

            $.post("{% url 'contentmgmt:rename_item' %}", {
                id: id,
                type: type,
                name: newName,
                csrfmiddlewaretoken: getCsrfToken()
            });
        }
    });

});
