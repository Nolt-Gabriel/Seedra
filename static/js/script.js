// Interatividade do SEEDRA: catálogo, movimentação e detalhes do item

// Estilos dos estados (abrir menu / filtro ativo). Ficam aqui para não depender do Tailwind.
(function injetarEstilos() {
    const estilo = document.createElement('style');
    estilo.textContent = `
        #c_btn.is-open, #filter_button.is-open {
            background: #587e49 !important; color: #fff !important; border-color: #587e49 !important;
        }
        #btn_deficit.is-active {
            background: #ef4444 !important; color: #fff !important; border-color: #ef4444 !important;
        }
        #c_arrow.is-open { transform: rotate(90deg); }
    `;
    document.head.appendChild(estilo);
})();


// ---------- Catálogo (catalogo.html) ----------
// Busca, categorias, ordenação e "Em déficit" funcionam juntos.
(function catalogo() {
    const busca = document.getElementById('c_search');
    const btnCategoria = document.getElementById('c_btn');
    const listaCategoria = document.getElementById('c_list');
    const setaCategoria = document.getElementById('c_arrow');
    const rotuloCategoria = document.getElementById('content_span');
    const btnFiltro = document.getElementById('filter_button');
    const menuFiltro = document.getElementById('opt_menu');
    const btnDeficit = document.getElementById('btn_deficit');

    // Não está na página do catálogo
    if (!btnCategoria || !btnFiltro) return;

    const tbody = document.querySelector('table tbody');
    const linhas = Array.from(tbody.querySelectorAll('tr.item_ok, tr.item_deficit'));
    const ordemOriginal = linhas.slice();

    const estado = { categoria: 'todas', soDeficit: false, termo: '' };

    const semAcento = (texto) => texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

    function aplicarFiltros() {
        linhas.forEach((tr) => {
            const nomes = semAcento(tr.cells[0].textContent + ' ' + tr.cells[1].textContent);
            const okCategoria = estado.categoria === 'todas' || tr.classList.contains('c_' + estado.categoria);
            const okDeficit = !estado.soDeficit || tr.classList.contains('item_deficit');
            const okBusca = !estado.termo || nomes.includes(estado.termo);
            tr.classList.toggle('hidden', !(okCategoria && okDeficit && okBusca));
        });
    }

    function ordenar(listaOrdenada) {
        listaOrdenada.forEach((tr) => tbody.appendChild(tr));
    }

    function fecharMenus() {
        listaCategoria.classList.add('hidden');
        btnCategoria.classList.remove('is-open');
        setaCategoria.classList.remove('is-open');
        menuFiltro.classList.add('hidden');
        btnFiltro.classList.remove('is-open');
    }

    function escolherCategoria(categoria, rotulo) {
        estado.categoria = categoria;
        rotuloCategoria.textContent = rotulo;
        aplicarFiltros();
        fecharMenus();
    }

    // Abrir/fechar menus
    btnCategoria.addEventListener('click', (e) => {
        e.stopPropagation();
        const abrir = listaCategoria.classList.contains('hidden');
        fecharMenus();
        if (abrir) {
            listaCategoria.classList.remove('hidden');
            btnCategoria.classList.add('is-open');
            setaCategoria.classList.add('is-open');
        }
    });

    btnFiltro.addEventListener('click', (e) => {
        e.stopPropagation();
        const abrir = menuFiltro.classList.contains('hidden');
        fecharMenus();
        if (abrir) {
            menuFiltro.classList.remove('hidden');
            btnFiltro.classList.add('is-open');
        }
    });

    document.addEventListener('click', fecharMenus);

    // Categorias
    document.getElementById('b_all').addEventListener('click', (e) => { e.stopPropagation(); escolherCategoria('todas', 'Todas as Categorias'); });
    document.getElementById('b_planta').addEventListener('click', (e) => { e.stopPropagation(); escolherCategoria('planta', 'Plantas'); });
    document.getElementById('b_semente').addEventListener('click', (e) => { e.stopPropagation(); escolherCategoria('semente', 'Sementes'); });

    // Ordenação
    document.getElementById('filter_all').addEventListener('click', (e) => {
        e.stopPropagation();
        ordenar(ordemOriginal);
        escolherCategoria('todas', 'Todas as Categorias');
    });

    const porNome = (a, b) => a.cells[0].textContent.trim().localeCompare(b.cells[0].textContent.trim(), 'pt-BR');

    document.getElementById('filter_AZ').addEventListener('click', (e) => {
        e.stopPropagation();
        ordenar(linhas.slice().sort(porNome));
        fecharMenus();
    });

    document.getElementById('filter_ZA').addEventListener('click', (e) => {
        e.stopPropagation();
        ordenar(linhas.slice().sort(porNome).reverse());
        fecharMenus();
    });

    // "Último Acesso": a tabela não tem essa informação, então só fecha o menu por enquanto.
    document.getElementById('filter_lastEntry').addEventListener('click', (e) => {
        e.stopPropagation();
        fecharMenus();
    });

    // Em déficit
    if (btnDeficit) {
        btnDeficit.addEventListener('click', (e) => {
            e.stopPropagation();
            estado.soDeficit = !estado.soDeficit;
            btnDeficit.classList.toggle('is-active', estado.soDeficit);
            aplicarFiltros();
        });
    }

    // Busca por nome comum ou científico
    if (busca) {
        busca.addEventListener('input', () => {
            estado.termo = semAcento(busca.value.trim());
            aplicarFiltros();
        });
    }
})();


// ---------- Movimentação (movimentacao.html) ----------
(function movimentacao() {
    const botaoLista = document.getElementById('btn_lista_planta');
    const lista = document.getElementById('lista_planta');

    // Não está na página de movimentação
    if (!botaoLista || !lista) return;

    const rotulo = document.getElementById('span_planta');
    const inputId = document.getElementById('item_id');
    const inputNome = document.getElementById('item_nome');

    botaoLista.addEventListener('click', (e) => {
        e.stopPropagation();
        lista.classList.toggle('hidden');
    });

    document.querySelectorAll('.opc_planta').forEach((botao) => {
        botao.addEventListener('click', (e) => {
            e.stopPropagation();
            rotulo.textContent = botao.dataset.nome;
            inputId.value = botao.dataset.id;
            inputNome.value = botao.dataset.nome;
            lista.classList.add('hidden');
        });
    });

    document.addEventListener('click', () => lista.classList.add('hidden'));
})();


// ---------- Botão excluir em catalogo/<id> ----------
function excluirItem(id) {
    if (!confirm('Tem certeza que deseja excluir esta espécie? Essa ação não pode ser desfeita.')) return;

    fetch(`/catalogo/excluir_item/${id}`, {
        method: 'DELETE'
    })
    .then((response) => {
        if (response.ok) {
            alert('Item excluído com sucesso!');
            window.location.href = '/catalogo';
        } else {
            alert('Erro ao excluir o item');
        }
    })
    .catch(() => alert('Erro de conexão ao excluir o item'));
}