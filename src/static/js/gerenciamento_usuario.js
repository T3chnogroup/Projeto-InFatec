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

 /*Alterar permissões dos usuários*/
  $('#alterarModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) 
    var id_user = button.data('usuario') 
    var modal = $(this) 
    var formulario = modal.find('form') 
    var action = formulario.attr('templete')
    action = action + id_user
    formulario.attr('action', action) 
    var pode_gerenciar = button.data('gerenciar')/*pega dados que estão salvos no botão*/
    var pode_criar = button.data('criarcanais')
    input_gerenciar = formulario.find('#gerenciar_usuarios')
    input_criarcanais = formulario.find('#criar_canais')
    if (pode_gerenciar == 1){
      //mudar input criar canal para checked
      input_gerenciar.prop( "checked", true );
    }
    else{
      //mudar input criar canal para não checked
      input_gerenciar.prop( "checked", false );
    }

    if (pode_criar == 1){
      //mudar input criar canal para checked
      input_criarcanais.prop( "checked", true );
    }
    else{
      //mudar input criar canal para não checked
      input_criarcanais.prop( "checked", false );
    }
  })
