var login_form = document.getElementById('login-form');
var signup_button = document.getElementById('signup');

if (signup_button) {
  signup_button.addEventListener('click', function() {
    window.location.href = 'signup.html';
  });
}

if (login_form) {
  login_form.addEventListener('submit', function(e) {
    e.preventDefault();
    try {
      let password = document.getElementById('password').value;
      let email = document.getElementById('email').value;

      if (password == "" || email == "") {
        alert('Preencha todos os campos');
        e.preventDefault();
        return;
      }

      if (!validateEmail(email)) {
        alert('Digite um email válido');
        e.preventDefault();
        return;
      }

      var login_btn = document.getElementById('login-btn');

      login_btn.innerHTML = `<div class="spinner-border text-light" role="status">
                                <span class="visually-hidden">Loading...</span>
                              </div>`;

      let xhttp = new XMLHttpRequest();

      xhttp.open("POST", server_url + '/login', true);
      xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      xhttp.send(JSON.stringify({
        password: password,
        email: email
      }));

      xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
          login_btn.innerHTML = 'Entrar';
          const response = JSON.parse(this.responseText);
          if (this.status == 200) {
            sessionStorage.setItem('user_id', response.user_id);
            sessionStorage.setItem('auth_token', response.access_token);
            window.location.href = 'home.html';
          } else{
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
      alert('Erro ao fazer login');
    }
  });
}