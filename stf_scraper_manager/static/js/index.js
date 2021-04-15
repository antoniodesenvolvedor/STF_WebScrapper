function populaHandsometable(dados) {
    let container = document.getElementById('grid_container');
    let hot = new Handsontable(container, {
    data:dados,
    rowHeaders: true,
    colHeaders: true,
    filters: true,
    dropdownMenu: true,
    language:'pt-BR',
    columnSorting: true,
    editor:false,
    licenseKey: 'non-commercial-and-evaluation',
});


}

dados = [['nome'],['antonio'],['simei']]
populaHandsometable(dados)
alert('olha eu aqui')





