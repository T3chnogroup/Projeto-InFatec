  $(document).ready(() => {
    $('#cpf').mask('000.000.000-00', {reverse: true});  
  })
  $('.botao-salvar').click(e => {
    $('#cpf').unmask();
    })