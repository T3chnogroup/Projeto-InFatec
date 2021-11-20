function delete_cookie( name, path, domain ) {
  if( get_cookie( name ) ) {
    document.cookie = name + "=" +
      ((path) ? ";path="+path:"")+
      ((domain)?";domain="+domain:"") +
      ";expires=Thu, 01 Jan 1970 00:00:01 GMT";
  }
}

$(document).ready(() => {
  let url = new URL(window.location.href);
  $('#id_usuario').val(url.searchParams.get("id_usuario"))
  $('.botao-enviar').click(e => {
    let senha1 = $('#senha1').val();
    let senha2 = $('#senha2').val();

    if (
      senha1.length < 3 || 
      senha2.length < 3 || 
      senha1 !== senha2
    ) {
      e.preventDefault();
    }

    if (senha1.length < 3) $('#senha1').addClass('is-invalid');
    else $('#email').removeClass('is-invalid');

    if (senha2.length < 3) $('#senha2').addClass('is-invalid');
    else $('#email').removeClass('is-invalid');

    if (senha1 !== senha2) $('#senha-validation-error').show();
     
    delete_cookie('changePassword')
  })
})