$(document).ready(() => {
  $('#btn_filtrar').click(e => {
    let titulo = $('#titulo').val()
    let data_inicial = $('#data_inicial').val()
    let data_final = $('#data_final').val()

    console.log(titulo === undefined)
    console.log(data_inicial.length < 3)
    console.log(data_final.length < 3)

    if (titulo.length < 3 && data_inicial.length < 3 && data_final.length < 3) {
      e.preventDefault();
      $('#erro-preenchimento').show();
    }

    if (titulo.length < 3) $('#titulo').addClass('is-invalid')
    else $('#titulo').removeClass('is-invalid')

    if (data_inicial.length < 3) $('#data_inicial').addClass('is-invalid')
    else $('#data_inicial').removeClass('is-invalid')

    if (data_final.length < 3) $('#data_final').addClass('is-invalid')
    else $('#data_final').removeClass('is-invalid')

  })
})