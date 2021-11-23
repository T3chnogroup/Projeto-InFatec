$(document).ready(() => {
  $('.botao-enviar').click(e => {
    let email = $('#email').val();
    let cookieExpireTime = new Date(Date.now() + 300000).toUTCString();

    if (
      email.length < 3 || 
      email.split('@')[1] !== 'fatec.sp.gov.br'
    ) {
      e.preventDefault();
    }

    if (email.length < 3) $('#email').addClass('is-invalid');
    else $('#email').removeClass('is-invalid');

    if (email.split('@')[1] !== 'fatec.sp.gov.br') {
      $('#email').addClass('is-invalid');
      $('#email-validation-error').show()
    } else {
      $('#email').removeClass('is-invalid');
    }
     
    document.cookie = `changePassword=True; expires=Thu, ${cookieExpireTime}`;
  })
})