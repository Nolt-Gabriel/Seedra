// Interatividade do Cadastro.html
{
    // botao de 'em Deficit'
    const item_deficit_table = document.querySelectorAll(".item_ok");
    const btn_deficit = document.getElementById("btn_deficit");

    btn_deficit.addEventListener('click', () => {
        item_deficit_table.forEach(item => {
            item.classList.toggle("hidden");
        });
        btn_deficit.classList.toggle('bg-red-500');
        btn_deficit.classList.toggle('text-white');
        btn_deficit.classList.toggle('hover:bg-red-400');
    });




    // botao de filtro
    const select_button = document.getElementById("filter_button");
    const select_menu = document.getElementById("opt_menu");
    

    select_button.addEventListener('click', (e) => {

        e.stopPropagation();
        select_menu.classList.toggle('hidden');
        select_button.classList.toggle('bg-[#587e49]');
        select_button.classList.toggle('text-white');

    })

    // botão de categorias
    const category_btn = document.getElementById('c_btn')
    const category_list = document.getElementById('c_list')
    const category_arrow = document.getElementById('c_arrow')

    category_btn.addEventListener('click', (e) => {

        e.stopPropagation();
        category_list.classList.toggle('hidden');
        category_btn.classList.toggle('bg-[#587e49]');
        category_btn.classList.toggle('text-white');
        category_arrow.classList.toggle('rotate-90');

    })

}