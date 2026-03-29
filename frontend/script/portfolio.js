const apiBase = '/api/v1/portfolio';

// ── DOM refs: portfolios ──────────────────────────────────────
const overlayCreate = document.getElementById('overlayCreate');
const openCreateBtn = document.getElementById('openCreate');
const fabCreate = document.getElementById('fabCreate');
const closeModalCreate = document.getElementById('closeModal');
const submitCreate = document.getElementById('submitCreate');
const refreshBtn = document.getElementById('refreshBtn');

const overlayUpdate = document.getElementById('overlayUpdate');
const closeModalUpdate = document.getElementById('closeModalUpdate');
const submitUpdate = document.getElementById('submitUpdate');

// ── DOM refs: positions drawer ────────────────────────────────
const drawerOverlay = document.getElementById('drawerOverlay');
const drawerClose = document.getElementById('drawerClose');
const drawerCloseBtn = document.getElementById('drawerCloseBtn');
const drawerTitle = document.getElementById('drawerTitle');
const positionsContent = document.getElementById('positionsContent');
const openAddAssetBtn = document.getElementById('openAddAsset');

// ── DOM refs: add asset modal ─────────────────────────────────
const overlayAddAsset = document.getElementById('overlayAddAsset');
const closeAddAsset = document.getElementById('closeAddAsset');
const submitAddAsset = document.getElementById('submitAddAsset');

// ── DOM refs: edit position modal ─────────────────────────────
const overlayEditPos = document.getElementById('overlayEditPosition');
const closeEditPos = document.getElementById('closeEditPosition');
const submitEditPos = document.getElementById('submitEditPosition');

// ── State ─────────────────────────────────────────────────────
let currentEditId = null;
let currentDrawerPortfolio = null;
let currentEditPosition = null;

// ══════════════════════════════════════════════════════════════
// Portfolio modals
// ══════════════════════════════════════════════════════════════

function openModalCreate() {
    overlayCreate.classList.add('open');
}

function closeModalFnCreate() {
    overlayCreate.classList.remove('open');
    document.getElementById('name').value = '';
    document.getElementById('currency').value = '';
}

openCreateBtn.addEventListener('click', openModalCreate);
fabCreate.addEventListener('click', openModalCreate);
closeModalCreate.addEventListener('click', closeModalFnCreate);
overlayCreate.addEventListener('click', e => {
    if (e.target === overlayCreate) closeModalFnCreate();
});

function openUpdateForm(portfolio) {
    currentEditId = portfolio.id;
    document.getElementById('nameUpdate').value = portfolio.name || '';
    document.getElementById('currencyUpdate').value = portfolio.currency || '';
    overlayUpdate.classList.add('open');
}

function closeModalFnUpdate() {
    overlayUpdate.classList.remove('open');
    document.getElementById('nameUpdate').value = '';
    document.getElementById('currencyUpdate').value = '';
    currentEditId = null;
}

closeModalUpdate.addEventListener('click', closeModalFnUpdate);
overlayUpdate.addEventListener('click', e => {
    if (e.target === overlayUpdate) closeModalFnUpdate();
});

refreshBtn.addEventListener('click', listItems);

// ══════════════════════════════════════════════════════════════
// Positions drawer
// ══════════════════════════════════════════════════════════════

function openDrawer(portfolio) {
    currentDrawerPortfolio = portfolio;
    drawerTitle.textContent = `Позиції: ${portfolio.name}`;
    drawerOverlay.classList.add('open');
    loadPositions(portfolio.id);
}

function closeDrawer() {
    drawerOverlay.classList.remove('open');
    currentDrawerPortfolio = null;
    positionsContent.innerHTML = '<p class="pos-empty">Завантаження...</p>';
}

drawerClose.addEventListener('click', closeDrawer);
drawerCloseBtn.addEventListener('click', closeDrawer);
drawerOverlay.addEventListener('click', e => {
    if (e.target !== drawerOverlay) return;
    // Do not close drawer if any modal is currently open on top
    const modalOpen = [overlayAddAsset, overlayEditPos, overlayCreate, overlayUpdate]
        .some(el => el.classList.contains('open'));
    if (modalOpen) return;
    closeDrawer();
});

async function loadPositions(portfolioId) {
    positionsContent.innerHTML = '<p class="pos-empty">Завантаження...</p>';
    try {
        const res = await apiFetch(`${apiBase}/${portfolioId}/positions`, {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        });

        if (!res.ok) {
            positionsContent.innerHTML = `<p class="pos-empty">Помилка завантаження: ${res.status}</p>`;
            return;
        }

        const positions = await res.json();

        if (positions.length === 0) {
            positionsContent.innerHTML = '<p class="pos-empty">Позицій немає. Додайте перший актив.</p>';
            return;
        }

        renderPositionsTable(positions);
    } catch (err) {
        console.error(err);
        positionsContent.innerHTML = '<p class="pos-empty">Помилка з\'єднання.</p>';
    }
}

function renderPositionsTable(positions) {
    const table = document.createElement('table');
    table.className = 'pos-table';

    table.innerHTML = `
      <thead>
        <tr>
          <th>Тікер</th>
          <th>Тип</th>
          <th>Кількість</th>
          <th>Сер. ціна</th>
          <th>Оновлено</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="posTableBody"></tbody>
    `;

    const tbody = table.querySelector('#posTableBody');

    positions.forEach(pos => {
        const ticker = pos.asset?.ticker ?? '—';
        const assetType = pos.asset?.asset_type ?? '';
        const qty = parseFloat(pos.quantity).toLocaleString('uk-UA', {maximumFractionDigits: 8});
        const avgPrice = parseFloat(pos.average_buy_price).toLocaleString('uk-UA', {
            minimumFractionDigits: 2, maximumFractionDigits: 4
        });
        const updatedAt = pos.updated_at
            ? new Date(pos.updated_at).toLocaleDateString('uk-UA')
            : '—';

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${ticker}</strong></td>
          <td><span class="badge">${assetType}</span></td>
          <td>${qty}</td>
          <td>${avgPrice}</td>
          <td style="opacity:.6; font-size:.82rem;">${updatedAt}</td>
          <td>
            <button class="btn warning btn-sm" data-action="edit" title="Оновити позицію">✏️</button>
          </td>
        `;

        tr.querySelector('[data-action="edit"]').addEventListener('click', () => {
            openEditPosition(pos, ticker);
        });

        tbody.appendChild(tr);
    });

    positionsContent.innerHTML = '';
    positionsContent.appendChild(table);
}

// ══════════════════════════════════════════════════════════════
// Add asset modal
// ══════════════════════════════════════════════════════════════

function openAddAssetModal() {
    document.getElementById('assetTicker').value = '';
    document.getElementById('assetQty').value = '';
    document.getElementById('assetPrice').value = '';
    overlayAddAsset.classList.add('open');
}

function closeAddAssetModal() {
    overlayAddAsset.classList.remove('open');
}

openAddAssetBtn.addEventListener('click', openAddAssetModal);
closeAddAsset.addEventListener('click', closeAddAssetModal);
overlayAddAsset.addEventListener('click', e => {
    if (e.target === overlayAddAsset) closeAddAssetModal();
});

submitAddAsset.addEventListener('click', async () => {
    const ticker = document.getElementById('assetTicker').value.trim().toUpperCase();
    const quantity = parseFloat(document.getElementById('assetQty').value);
    const price = parseFloat(document.getElementById('assetPrice').value);

    if (!ticker) {
        alert('Введіть тікер');
        return;
    }
    if (isNaN(quantity) || quantity <= 0) {
        alert('Введіть коректну кількість');
        return;
    }
    if (isNaN(price) || price <= 0) {
        alert('Введіть коректну ціну');
        return;
    }
    if (!currentDrawerPortfolio) {
        alert('Портфель не вибраний');
        return;
    }

    submitAddAsset.disabled = true;
    try {
        const res = await apiFetch(`${apiBase}/${currentDrawerPortfolio.id}/assets`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ticker, quantity, price_per_share: price})
        });
        if (!res.ok) {
            const txt = await res.text().catch(() => res.statusText);
            alert('Помилка додавання: ' + res.status + ' ' + txt);
            return;
        }
        closeAddAssetModal();
        await loadPositions(currentDrawerPortfolio.id);
    } catch (err) {
        console.error(err);
        alert('Помилка з\'єднання');
    } finally {
        submitAddAsset.disabled = false;
    }
});

// ══════════════════════════════════════════════════════════════
// Edit position modal
// ══════════════════════════════════════════════════════════════

function openEditPosition(position, ticker) {
    currentEditPosition = {...position, ticker};
    document.getElementById('editPositionMeta').textContent =
        `Поточна кількість: ${parseFloat(position.quantity)} · Середня ціна: ${parseFloat(position.average_buy_price)}`;
    document.getElementById('editTicker').value = ticker;
    document.getElementById('editQty').value = '';
    document.getElementById('editPrice').value = '';
    overlayEditPos.classList.add('open');
}

function closeEditPositionModal() {
    overlayEditPos.classList.remove('open');
    currentEditPosition = null;
}

closeEditPos.addEventListener('click', closeEditPositionModal);
overlayEditPos.addEventListener('click', e => {
    if (e.target === overlayEditPos) closeEditPositionModal();
});

submitEditPos.addEventListener('click', async () => {
    const quantity = parseFloat(document.getElementById('editQty').value);
    const price = parseFloat(document.getElementById('editPrice').value);

    if (isNaN(quantity) || quantity <= 0) {
        alert('Введіть коректну кількість');
        return;
    }
    if (isNaN(price) || price <= 0) {
        alert('Введіть коректну ціну');
        return;
    }
    if (!currentDrawerPortfolio || !currentEditPosition) {
        alert('Дані не знайдено');
        return;
    }

    submitEditPos.disabled = true;
    try {
        // POST /{portfolio_id}/assets — upserts position via new BUY transaction
        const res = await apiFetch(`${apiBase}/${currentDrawerPortfolio.id}/assets`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                ticker: currentEditPosition.ticker,
                quantity,
                price_per_share: price
            })
        });
        if (!res.ok) {
            const txt = await res.text().catch(() => res.statusText);
            alert('Помилка оновлення: ' + res.status + ' ' + txt);
            return;
        }
        closeEditPositionModal();
        await loadPositions(currentDrawerPortfolio.id);
    } catch (err) {
        console.error(err);
        alert('Помилка з\'єднання');
    } finally {
        submitEditPos.disabled = false;
    }
});

// ══════════════════════════════════════════════════════════════
// Portfolio CRUD
// ══════════════════════════════════════════════════════════════

async function listItems() {
    const grid = document.getElementById('itemsGrid');
    const empty = document.getElementById('emptyState');
    grid.innerHTML = 'Завантаження...';
    try {
        const res = await apiFetch(apiBase + '/', {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        });
        if (!res.ok) {
            grid.innerHTML = '';
            empty.style.display = 'block';
            empty.textContent = 'Помилка отримання портфелів: ' + res.status + ' ' + res.statusText;
            return;
        }
        const data = await res.json();
        grid.innerHTML = '';
        if (!Array.isArray(data) || data.length === 0) {
            empty.style.display = 'block';
            return;
        }
        empty.style.display = 'none';

        data.forEach(it => {
            const card = document.createElement('article');
            card.className = 'card';

            const h = document.createElement('h3');
            h.textContent = it.name || 'Без назви';
            const p = document.createElement('p');
            p.textContent = it.currency ? `Валюта: ${it.currency}` : '';
            card.appendChild(h);
            card.appendChild(p);

            const actions = document.createElement('div');
            actions.className = 'card-actions';

            const posBtn = document.createElement('button');
            posBtn.className = 'btn';
            posBtn.textContent = '📊 Позиції';
            posBtn.onclick = () => openDrawer(it);

            const updateBtn = document.createElement('button');
            updateBtn.className = 'btn warning';
            updateBtn.textContent = 'Оновити';
            updateBtn.onclick = () => openUpdateForm(it);

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn danger';
            deleteBtn.textContent = 'Видалити';
            deleteBtn.onclick = async () => {
                if (!confirm('Видалити портфель?')) return;
                deleteBtn.disabled = true;
                try {
                    const res = await apiFetch(apiBase + '/' + it.id, {method: 'DELETE'});
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

            actions.appendChild(posBtn);
            actions.appendChild(updateBtn);
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
    const res = await apiFetch(apiBase + '/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, currency, is_imported})
    });
    if (!res.ok) {
        const txt = await res.text().catch(() => res.statusText);
        alert('Помилка створення: ' + res.status + ' ' + txt);
        return false;
    }
    return true;
}

async function updateItem(id, {name, currency}) {
    const res = await apiFetch(apiBase + '/' + id, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, currency})
    });
    if (!res.ok) {
        const txt = await res.text().catch(() => res.statusText);
        alert('Помилка оновлення: ' + res.status + ' ' + txt);
        return false;
    }
    return true;
}

submitCreate.addEventListener('click', async (e) => {
    e.preventDefault();
    const name = document.getElementById('name').value.trim();
    const currency = document.getElementById('currency').value.trim() || 'USD';
    if (!name) {
        alert('Будь ласка, введіть назву');
        return;
    }
    submitCreate.disabled = true;
    try {
        const ok = await createItem({name, currency, is_imported: false});
        if (ok) {
            closeModalFnCreate();
            await listItems();
        }
    } finally {
        submitCreate.disabled = false;
    }
});

submitUpdate.addEventListener('click', async (e) => {
    e.preventDefault();
    const name = document.getElementById('nameUpdate').value.trim();
    const currency = document.getElementById('currencyUpdate').value.trim();
    if (!name) {
        alert('Будь ласка, введіть назву');
        return;
    }
    if (!currency) {
        alert('Будь ласка, введіть валюту');
        return;
    }
    if (!currentEditId) {
        alert('Не вибрано портфель');
        return;
    }
    submitUpdate.disabled = true;
    try {
        const ok = await updateItem(currentEditId, {name, currency});
        if (ok) {
            closeModalFnUpdate();
            await listItems();
        }
    } finally {
        submitUpdate.disabled = false;
    }
});

// initial load
listItems();