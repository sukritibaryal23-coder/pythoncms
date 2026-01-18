// CSRF helper
function getCookie(name) {
    let cookieValue = null;
    document.cookie.split(";").forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
    });
    return cookieValue;
}

// Drag & Drop
new Sortable(document.getElementById('media-table-body'), {
    handle: '.drag-handle',
    animation: 150,
    onEnd: function(evt){
        const order = Array.from(evt.to.children).map(tr => tr.dataset.id);
        fetch('/media/reorder/', {
            method: 'POST',
            headers: {
                'Content-Type':'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({order: order})
        });
    }
});

// Toggle status
document.addEventListener('click', function(e){
    if(!e.target.classList.contains('toggle-status-btn')) return;
    const btn = e.target;
    fetch(`/media/toggle-status/${btn.dataset.id}/`, {
        method:'POST',
        headers:{
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With':'XMLHttpRequest'
        }
    })
    .then(res=>res.json())
    .then(data=>{
        if(data.success){
            btn.classList.toggle('btn-success', data.status);
            btn.classList.toggle('btn-secondary', !data.status);
            btn.textContent = data.status?'Published':'Unpublished';
        }
    });
});

// Delete single
document.addEventListener('click', function(e){
    if(!e.target.classList.contains('delete-media-btn')) return;
    const btn = e.target;
    if(!confirm('Delete this media?')) return;
    fetch(`/media/delete/${btn.dataset.id}/`, {
        method:'POST',
        headers:{'X-CSRFToken':getCookie('csrftoken'),'X-Requested-With':'XMLHttpRequest'}
    })
    .then(res=>res.json())
    .then(data=>{ if(data.success) btn.closest('tr').remove(); });
});

// Bulk actions
document.querySelectorAll('.bulk-btn').forEach(btn=>{
    btn.addEventListener('click', function(){
        const action = btn.dataset.action;
        const selected = [...document.querySelectorAll('input[name="selected_media"]:checked')].map(i=>i.value);
        if(!selected.length) return alert('Select at least one item');
        const formData = new FormData();
        formData.append('action', action);
        selected.forEach(id=>formData.append('selected_media[]', id));
        fetch('/media/bulk-action/', {
            method:'POST',
            body: formData,
            headers:{'X-CSRFToken':getCookie('csrftoken'),'X-Requested-With':'XMLHttpRequest'}
        }).then(res=>res.json()).then(()=>location.reload());
    });
});

// Search / filter
document.getElementById('media-search-form').addEventListener('submit', function(e){
    e.preventDefault();
    const query = document.getElementById('media-search').value;
    const params = new URLSearchParams(window.location.search);
    params.set('q', query);
    params.set('page', 1);
    fetch(`/media/?${params.toString()}`, {headers:{'X-Requested-With':'XMLHttpRequest'}})
        .then(res=>res.json())
        .then(data=>document.getElementById('media-table-body').innerHTML=data.html);
});

// Media type filter
document.getElementById('media-type-filter').addEventListener('change', function(){
    const type = this.value;
    const params = new URLSearchParams(window.location.search);
    params.set('type', type);
    window.location.search = params.toString();
});

// Select all
document.getElementById('select-all').addEventListener('click', function(){
    document.querySelectorAll('input[name="selected_media"]').forEach(cb=>cb.checked=this.checked);
});

