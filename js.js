$(document).ready(function()
{
	var botao = $ ('.bt1');//classe no a que vai ser clicado
	var dropDown = $('.ul-pesquisa');//classe do submenu que vai abrir
	botao.on('click', function(event)
	{
		dropDown.stop(true,true).slideToggle();
		event.stopPropagation();
	});
});