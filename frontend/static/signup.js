var signup_form = document.getElementById('signup-form');
var signup_back_button = document.getElementById('signup-back');

if (signup_form) {
  signup_form.addEventListener('submit', function(e) {
    e.preventDefault();
    try {

      let username = document.getElementById('name').value;
      let password = document.getElementById('password').value;
      let confirm_password = document.getElementById('confirm-password').value;

      if (password != confirm_password) {
        alert('Senhas não coincidem');
        return;
      }

      let email = document.getElementById('email').value;

      if (username == "" || password == "" || email == "") {
        alert('Preencha todos os campos');
        return;
      }

      if (!validateEmail(email)) {
        alert('Digite um email válido');
        return;
      }

      var signup_btn = document.getElementById('signup-btn');

      signup_btn.innerHTML = `<div class="spinner-border text-light" role="status">
                                <span class="visually-hidden">Loading...</span>
                              </div>`;

      let xhttp = new XMLHttpRequest();

      xhttp.open("POST", server_url + '/register', true);
      xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      xhttp.send(JSON.stringify({
        username: username,
        password: password,
        email: email
      }));

      xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
          signup_btn.innerHTML = 'Cadastrar';
          if (this.status == 201) {
            alert('Usuário criado com sucesso');
            window.location.href = 'index.html';
          } else{
            const response = JSON.parse(this.responseText);
            if (response.error) {
              alert(response.error);
            } else if (response.msg) {
              alert(response.msg);
            } else if (response.message) {
              alert(response.message);
            } else {
              alert('Erro desconhecido');
            }
          }
        }
      };
    } catch (error) {
      console.error(error);
      alert('Erro ao cadastrar usuário');
    }
  });
}

if (signup_back_button) {
  signup_back_button.addEventListener('click', function() {
    window.location.href = 'index.html';
  });
}