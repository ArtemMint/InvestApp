const apiBase = '/api/v1/portfolio';

// token may change during session; tokens are stored as HttpOnly cookie for production


// UI helpers
const overlay = document.getElementById('overlay');
const openCreate = document.getElementById('openCreate');
const fabCreate = document.getElementById('fabCreate');
const closeModal = document.getElementById('closeModal');
const submitCreate = document.getElementById('submitCreate');
const refreshBtn = document.getElementById('refreshBtn');

function openModal() {
    overlay.classList.add('open')
}

function closeModalFn() {
    overlay.classList.remove('open')
}

openCreate.addEventListener('click', openModal);
fabCreate.addEventListener('click', openModal);
closeModal.addEventListener('click', closeModalFn);
overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeModalFn();
});

refreshBtn.addEventListener('click', listItems);

async function listItems() {
    const grid = document.getElementById('itemsGrid');
    const empty = document.getElementById('emptyState');
    grid.innerHTML = 'Завантаження...';
    try {
        const res = await apiFetch(apiBase + '/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!res.ok) {
            grid.innerHTML = '';
            empty.style.display = 'block';
            empty.textContent = 'Помилка отримання портфелів: ' + res.status + res.statusText;
            return;
        }
        const data = await res.json();
        grid.innerHTML = '';
        if (!Array.isArray(data) || data.length === 0) {
            empty.style.display = 'block';
            return;
        } else {
            empty.style.display = 'none';
        }

        data.forEach(it => {
            const card = document.createElement('article');
            card.className = 'card';

            const h = document.createElement('h3');
            h.textContent = it.name || 'Без назви';
            const p = document.createElement('p');
            p.textContent = it.currency ? `Валюта: ${it.currency}` : '';
            card.appendChild(h);
            card.appendChild(p);

            // Create actions container
            const actions = document.createElement('div');
            actions.className = 'card-actions';

            // Create delete button
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn danger';
            deleteBtn.textContent = 'Видалити';
            deleteBtn.setAttribute('aria-label', 'Видалити елемент');
            deleteBtn.onclick = async () => {
                if (!confirm('Ви впевнені, що хочете видалити цей портфель?')) return;
                deleteBtn.disabled = true;
                try {
                    const res = await apiFetch(apiBase + '/' + it.id, {
                        method: 'DELETE'
                    });
                    if (!res.ok) {
                        alert('Не вдалося видалити: ' + res.status);
                    } else {
                        await listItems();
                    }
                } catch (err) {
                    console.error(err);
                    alert('Помилка видалення');
                } finally {
                    deleteBtn.disabled = false;
                }
            };
            actions.appendChild(deleteBtn);

            card.appendChild(actions);
            grid.appendChild(card);
        });
    } catch (err) {
        grid.innerHTML = '';
        empty.style.display = 'block';
        empty.textContent = 'Fetch error';
    }
}

async function createItem({name, currency, is_imported}) {
    const payload = {name, currency, is_imported};
    const res = await apiFetch(apiBase + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    if (!res.ok) {
        const txt = await res.text().catch(() => res.statusText);
        alert('Помилка створення: ' + res.status + ' ' + txt);
        return false;
    }
    return true;
}

submitCreate.addEventListener('click', async (e) => {
    e.preventDefault();
    const name = document.getElementById('name').value.trim();
    // Map UI fields to backend portfolio model: use name as name, currency fixed to USD for now
    const currency = 'USD';
    const is_imported = false;

    if (!name) {
        alert('Будь ласка, введіть назву');
        return;
    }

    // prevent double submissions
    submitCreate.disabled = true;
    try {
        const ok = await createItem({name, currency, is_imported});
        if (ok) {
            // reset form
            document.getElementById('name').value = '';
            closeModalFn();
            await listItems();
        }
    } finally {
        submitCreate.disabled = false;
    }
});

// initial load
listItems();
