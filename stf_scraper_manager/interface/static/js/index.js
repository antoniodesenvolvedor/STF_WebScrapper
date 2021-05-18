let intervalCheckProgress = null

function loadBar(id_busca, key_word){
    intervalCheckProgress =  setInterval(function(){ checkProgress(id_busca,key_word); }, 3000);
}


function checkProgress(id_busca, key_word){
    console.log('Checking progress...')
    fetch('/return_progress?id_busca='+id_busca+'&key_word=' + key_word)
      .then(response => response.json())
      .then(data => updateProgressBar(data,key_word));
}

function updateProgressBar(data, key_word){
    progressValue = data.progress
    inicio_processamento = data.inicio_processamento
    document.querySelector('#progress_bar').value = progressValue
    document.querySelector('#inicio_processamento').innerHTML = 'Inicio processamento:' + inicio_processamento

    if(progressValue == 100){
        clearInterval(intervalCheckProgress);
        location.href= '/?key_word=' + key_word
    }
}




//dados = [['carlos',30],['antonio',29],['simei',31]]
//colunas = ['nome', 'idade']
//
//populaHandsometable(colunas, dados)

//populaHandsometable(dados)






