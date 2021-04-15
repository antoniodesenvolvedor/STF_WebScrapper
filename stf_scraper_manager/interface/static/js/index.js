function populaHandsometable(cabecalho, dados) {
    console.log('hand')
    let container = document.getElementById('grid_container');
    let hot = new Handsontable(container, {
    data: dados,
    rowHeaders: true,
    colHeaders: cabecalho,
    filters: true,
    dropdownMenu: true,
//    language:'pt-BR',
    columnSorting: true,
    editor:false,
    licenseKey: 'non-commercial-and-evaluation',
});


}



//dados = [['carlos',30],['antonio',29],['simei',31]]
//colunas = ['nome', 'idade']
//
//populaHandsometable(colunas, dados)

//populaHandsometable(dados)






