$(document).ready(() => {
  $('#cpf').mask('000.000.000-00', {reverse: true});

  $('.botao-enviar').click(e => {
    $('#cpf').unmask();

    let nome = $('#nome').val();
    let email = $('#email').val();
    let cpf = $('#cpf').val();
    let password = $('#password').val();
    let confirmacao_senha = $('#confirmacao_senha').val();

    if (
      nome.length < 3 ||
      email.length < 3 ||
      cpf.length !== 11 ||
      !validateCpf(cpf) ||
      password.length < 4 ||
      confirmacao_senha.length < 4 ||
      email.split('@')[1] !== 'fatec.sp.gov.br'
    ) {
      e.preventDefault();
    }
    
    if (nome.length < 3) $('#nome').addClass('is-invalid')
    else $('#nome').removeClass('is-invalid')

    if (email.length < 3) $('#email').addClass('is-invalid');
    else $('#email').removeClass('is-invalid');

    if (email.split('@')[1] !== 'fatec.sp.gov.br') {
      $('#email').addClass('is-invalid');
      $('#email-validation-error').show()
    } else {
      $('#email').removeClass('is-invalid');
    }

    if (cpf.length !== 11) {
      $('#cpf').mask('000.000.000-00', {reverse: true});
      $('#cpf').addClass('is-invalid')
    }
    else  $('#cpf').removeClass('is-invalid');

    if (!validateCpf(cpf)) {
      $('#cpf').mask('000.000.000-00', {reverse: true});
      $('#cpf').addClass('is-invalid')
      $('#cpf-validation-error').show()
    }
    else  $('#cpf').removeClass('is-invalid');

    if (password.length < 4) $('#password').addClass('is-invalid');
    else $('#password').removeClass('is-invalid');

    if (confirmacao_senha.length < 4) $('#confirmacao_senha').addClass('is-invalid');
    else $('#confirmacao_senha').removeClass('is-invalid');


  })
}) 


function botao_fechar_msg_sucesso() {
  document.getElementById('cadastro').classList.remove('show');/*função do botão de fechar mensagem de sucesso*/
}


const togglePassword = document.querySelector("#togglePassword");
const password = document.querySelector("#password");

togglePassword.addEventListener("click", function () {

  // toggle the type attribute
  const type = password.getAttribute("type") === "password" ? "text" : "password";
  password.setAttribute("type", type);
  // toggle the eye icon
  this.classList.toggle('bi-eye');
  this.classList.toggle('bi-eye-slash');
});

const toggleConfirmacao_senha = document.querySelector("#toggleConfirmacao_senha");
const confirmacao_senha = document.querySelector("#confirmacao_senha");

toggleConfirmacao_senha.addEventListener("click", function () {

  // toggle the type attribute
  const type = confirmacao_senha.getAttribute("type") === "password" ? "text" : "password";
  confirmacao_senha.setAttribute("type", type);
  // toggle the eye icon
  this.classList.toggle('bi-eye');
  this.classList.toggle('bi-eye-slash');
});
