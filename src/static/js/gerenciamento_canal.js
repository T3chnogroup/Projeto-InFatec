$(document).ready(function () {
    $('.adicionar-membros').select2({
      placeholder: "Adicionar participante"
    });
  });

  $(".select-funcao").change(function (event) {
    console.log($(this).val())
    var dados = $(this).val()
    var posicao_primeiro_espaco = dados.indexOf(' ')
    var usuario = dados.substring(0, posicao_primeiro_espaco)
    dados = dados.substring(posicao_primeiro_espaco + 3)
    posicao_primeiro_espaco = dados.indexOf(' ')
    var canal = dados.substring(0, posicao_primeiro_espaco)
    dados = dados.substring(posicao_primeiro_espaco + 3)
    posicao_primeiro_espaco = dados.indexOf(' ')
    var funcao_de = dados.substring(0, posicao_primeiro_espaco)
    dados = dados.substring(posicao_primeiro_espaco + 3)
    var funcao_para = dados
    var url = `/editar-funcao-membro-canal?usuario=${usuario}&canal=${canal}&funcao=${funcao_para}`

    window.location.href = url
  });

/*Remover participante do canal*/
  $('#excluirModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) /*Botão que foi clicado*/
    var id_user = button.data('usuario') /*Atribui à variável o atributo data-usuario do botão que foi clicado*/
    var modal = $(this) /*Modal que está sendo aberto*/
    var formulario = modal.find('form') /*Atribui à variável formulário o formulário que foi encontrado no modal*/
    var action = formulario.attr('templete')
    action = action + id_user /*Action monta a URL completa com o id do usuário*/
    formulario.attr('action', action) /*Coloca a URL completa no action do formulário*/
  })

/*Função de pesquisar membros do canal*/
  $('#pesquisar_membros').keyup(function() {
    var texto = $(this).val().toLowerCase()
    $('.linha-pesquisada').each(function() {
     var nome = $($(this).find('td')[0]).text().toLowerCase()
     var email = $($(this).find('td')[1]).text().toLowerCase()
     $(this).addClass('d-none')
     if (nome.indexOf(texto)>=0){
       $(this).removeClass('d-none')
     }
     if (email.indexOf(texto)>=0){
       $(this).removeClass('d-none')
     }
    }
    )
  }
  )