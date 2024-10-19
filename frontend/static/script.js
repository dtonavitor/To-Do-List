var login_form = document.getElementById('login-form');
var signup_form = document.getElementById('signup-form');
var signup_button = document.getElementById('signup');
var signup_back_button = document.getElementById('signup-back');
var logout_button = document.getElementById('logout');

if (logout_button) {
  logout_button.addEventListener('click', function() {
    window.location.href = 'index.html';
  });
}

if (signup_back_button) {
  signup_back_button.addEventListener('click', function() {
    window.location.href = 'index.html';
  });
}

if (signup_button) {
  signup_button.addEventListener('click', function() {
    window.location.href = 'signup.html';
  });
}

if (login_form) {
  login_form.addEventListener('submit', function(e) {
    window.location.href = 'home.html';
    e.preventDefault();
  });
}

if (signup_form) {
  signup_form.addEventListener('submit', function(e) {
    window.location.href = 'login.html';
    e.preventDefault();
  });
}