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


(function catalogo() {
    const busca = document.getElementById('c_search');
    const btnCategoria = document.getElementById('c_btn');
    const listaCategoria = document.getElementById('c_list');
    const setaCategoria = document.getElementById('c_arrow');
    const rotuloCategoria = document.getElementById('content_span');
    const btnFiltro = document.getElementById('filter_button');
    const menuFiltro = document.getElementById('opt_menu');
    const btnDeficit = document.getElementById('btn_deficit');

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

    document.getElementById('b_all').addEventListener('click', (e) => { e.stopPropagation(); escolherCategoria('todas', 'Todas as Categorias'); });
    document.getElementById('b_planta').addEventListener('click', (e) => { e.stopPropagation(); escolherCategoria('planta', 'Plantas'); });
    document.getElementById('b_semente').addEventListener('click', (e) => { e.stopPropagation(); escolherCategoria('semente', 'Sementes'); });

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

    document.getElementById('filter_lastEntry').addEventListener('click', (e) => {
        e.stopPropagation();
        fecharMenus();
    });

    if (btnDeficit) {
        btnDeficit.addEventListener('click', (e) => {
            e.stopPropagation();
            estado.soDeficit = !estado.soDeficit;
            btnDeficit.classList.toggle('is-active', estado.soDeficit);
            aplicarFiltros();
        });
    }

    if (busca) {
        busca.addEventListener('input', () => {
            estado.termo = semAcento(busca.value.trim());
            aplicarFiltros();
        });
    }
})();


(function movimentacao() {
    const botaoLista = document.getElementById('btn_lista_planta');
    const lista = document.getElementById('lista_planta');

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


function excluirItem(id) {
    if (!confirm('Tem certeza que deseja prosseguir com a exclusão desta espécie?')) return;

    fetch(`/catalogo/excluir_item/${id}`, {
        method: 'DELETE'
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error('Erro na requisição');
        }
        return response.json();
    })
    .then((dados) => {
        alert(dados.mensagem);
        window.location.href = '/catalogo';
    })
    .catch(() => alert('Erro ao tentar excluir o item'));
}


const ESCALA_MIN = 90;
const ESCALA_MAX = 130;
const ESCALA_PADRAO = 100;

function aplicarEscalaFonte(escala) {
    const valorLimitado = Math.min(ESCALA_MAX, Math.max(ESCALA_MIN, escala));
    document.documentElement.style.fontSize = valorLimitado + '%';
    localStorage.setItem('seedra-font-scale', valorLimitado);
}

function alterarFonte(delta) {
    const atual = parseInt(localStorage.getItem('seedra-font-scale') || ESCALA_PADRAO, 10);
    aplicarEscalaFonte(atual + delta);
}

function resetarFonte() {
    aplicarEscalaFonte(ESCALA_PADRAO);
}

function atualizarIconeTema(tema) {
    const icone = document.getElementById('icone-tema');
    const botao = document.getElementById('btn-tema');
    if (icone) {
        if (tema === 'dark') {
            icone.classList.remove('fa-moon');
            icone.classList.add('fa-sun');
        } else {
            icone.classList.remove('fa-sun');
            icone.classList.add('fa-moon');
        }
    }
    if (botao) {
        botao.title = tema === 'dark' ? 'Alternar para modo claro' : 'Alternar para modo escuro';
    }
}

function alternarTema() {
    const temaAtual = document.documentElement.getAttribute('data-theme') || 'light';
    const novoTema = temaAtual === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', novoTema);
    localStorage.setItem('seedra-theme', novoTema);
    atualizarIconeTema(novoTema);
}


function aceitarCookiesLGPD() {
    localStorage.setItem('seedra-lgpd-cookies', 'aceito');
    const banner = document.getElementById('banner-lgpd');
    if (banner) banner.classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
    const temaSalvo = localStorage.getItem('seedra-theme') || 'light';
    atualizarIconeTema(temaSalvo);

    const banner = document.getElementById('banner-lgpd');
    if (banner && !localStorage.getItem('seedra-lgpd-cookies')) {
        banner.classList.remove('hidden');
    }
});