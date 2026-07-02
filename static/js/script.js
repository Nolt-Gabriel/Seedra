// Interatividade do Cadastro.html
// Botão em déficit
{
    // botao de 'em Deficit'
    const item_deficit_table_ok = document.querySelectorAll(".item_ok");
    const item_deficit_table = document.querySelectorAll(".item_deficit");
    const btn_deficit = document.getElementById("btn_deficit");

    if (btn_deficit) {
        btn_deficit.addEventListener('click', (e) => {
            e.stopPropagation();
            item_deficit_table_ok.forEach(item => {
                item.classList.toggle("hidden");
                item.classList.toggle('transform-discrete');
            });
            item_deficit_table.forEach(item => {
                item.classList.remove("hidden")
            })

            btn_deficit.classList.toggle('bg-red-500');
            btn_deficit.classList.toggle('text-white');
            btn_deficit.classList.toggle('hover:bg-red-400');
        });

    }
        
}

{
        // botao de filtro
    
    const select_menu = document.getElementById("opt_menu");

    const filter_button = document.getElementById("filter_button");
    const filter_span = document.getElementById("filter_span");

    const filter_all = document.getElementById("filter_all");

    const filter_AZ = document.getElementById("filter_AZ");
    const filter_order_normal = document.getElementById("list_order_normal");
    const filter_ZA = document.getElementById("filter_ZA");


    const filter_lastEntry = document.getElementById("filter_lastEntry");
    
    if (filter_button) {
        filter_button.addEventListener('click', (e) => {

            e.stopPropagation();
            select_menu.classList.toggle('hidden');
            filter_button.classList.toggle('bg-[#587e49]');
            filter_button.classList.toggle('text-white');

        })
    }
}

// Botão de Categorias / catalogo.html
{  
    // botão de categorias
    const category_span = document.getElementById('content_span')

    const category_btn = document.getElementById('c_btn');
    const category_list = document.getElementById('c_list');
    const category_arrow = document.getElementById('c_arrow');

    const btn_category_all = document.getElementById('b_all');
    const btn_category_planta = document.getElementById('b_planta');
    const btn_category_semente = document.getElementById('b_semente');

    const category_planta = document.querySelectorAll('.c_planta');
    const category_semente = document.querySelectorAll('.c_semente');

    const item_deficit_table_ok = document.querySelectorAll(".item_ok");
    const item_deficit_table = document.querySelectorAll(".item_deficit");

    if (category_btn || btn_category_all || btn_category_planta || btn_category_semente) {
        category_btn.addEventListener('click', (e) => {

            e.stopPropagation();

            category_list.classList.toggle('hidden');
            category_btn.classList.toggle('bg-[#587e49]');
            category_btn.classList.toggle('text-white');
            category_arrow.classList.toggle('rotate-90');

        })
    
        btn_category_all.addEventListener('click', (e) => {

            e.stopPropagation();

            category_planta.forEach(planta => {planta.classList.remove('hidden')});
            category_semente.forEach(semente => {semente.classList.remove('hidden')});

            category_span.textContent = 'Todas as Categorias'
            category_list.classList.toggle('hidden');
        })

        btn_category_planta.addEventListener('click', (e) => {

            e.stopPropagation();

            category_semente.forEach(semente => {semente.classList.toggle('hidden');
            });
            category_planta.forEach(planta => {planta.classList.remove('hidden'); });
            
            category_span.textContent = "Plantas"
            category_list.classList.toggle('hidden');
        })

        btn_category_semente.addEventListener('click', (e) => {
            
            e.stopPropagation();

            category_semente.forEach(semente => {semente.classList.remove('hidden')});
            category_planta.forEach(planta => {planta.classList.toggle('hidden')});

            category_span.textContent = "Sementes"
            category_list.classList.toggle('hidden');
        })
    
    }
}

{

    const btn_list_planta = document.getElementById('btn_lista_planta');
    const list_planta = document.getElementById('lista_planta');

    btn_list_planta.addEventListener('click', (e) => {
        e.stopPropagation();
        console.log('clicou');
        list_planta.classList.toggle('hidden');
    })

    const spam_planta = document.getElementById("span_planta");
    const input_planta = document.getElementById("item_id");
    const input_nome_planta = document.getElementById("item_nome");

    document.querySelectorAll(".opc_planta").forEach(botao => {

        botao.addEventListener('click', (e) => {

            e.stopPropagation();
            spam_planta.textContent = botao.dataset.nome;
            input_planta.value = botao.dataset.id;
            input_nome_planta.value = botao.dataset.nome;
            
            lista_planta.classList.add('hidden');


        })

    })
    
}

