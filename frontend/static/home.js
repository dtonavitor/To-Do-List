var logout_button = document.getElementById('logout');

var auth_token = sessionStorage.getItem('auth_token');

var task_id = null;

document.getElementById('update-name').value = document.getElementById('name').value;

if (!auth_token) {
  window.location.href = 'index.html';
}

const logout = () => {
  try {
    let xhttp = new XMLHttpRequest();
    xhttp.open("GET", server_url + '/logout', true);
    xhttp.setRequestHeader("Authorization", "Bearer " + auth_token);

    xhttp.send();

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 200) {
          sessionStorage.removeItem('auth_token');
          sessionStorage.removeItem('user_id');
          window.location.href = 'index.html';
        } else {
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
    alert('Erro ao fazer logout');
  }
}
if (logout_button) {
  logout_button.addEventListener('click', logout);
}

const update_status = (task_id) => {
  try {
    let current_status = document.getElementById(`${task_id}-status`).innerText;
    let new_status = current_status == 'pendente' ? 'completa' : 'pendente';

    let xhttp = new XMLHttpRequest();
    xhttp.open("PUT", server_url + '/task/status/' + task_id, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.setRequestHeader("Authorization", "Bearer " + auth_token);
    xhttp.setRequestHeader("Access-Control-Allow-Origin", "*");

    xhttp.send(JSON.stringify({
      status: new_status
    }));

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 200) {
          alert('Status atualizado com sucesso');
          window.location.reload();
        } else {
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
    alert('Erro ao atualizar status');
  }
}

const delete_task = (task_id) => {
  try {
    let xhttp = new XMLHttpRequest();

    xhttp.open("DELETE", server_url + '/task/' + task_id, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.setRequestHeader("Authorization", "Bearer " + auth_token);

    xhttp.send();

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 200) {
          alert('Tarefa deletada com sucesso');
          window.location.reload();
        } else {
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
    alert('Erro ao deletar tarefa');
  }
}

window.onload = function() {
  try {
    let xhttp = new XMLHttpRequest();
    let user_id = sessionStorage.getItem('user_id');
    xhttp.open("GET", server_url + '/tasks/' + user_id, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.setRequestHeader("Authorization", "Bearer " + auth_token);
    xhttp.send();

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 200) {
          const response = JSON.parse(this.responseText);
          const tasks = response.tasks;
          let tasks_html = '';
          tasks.forEach((task) => {
            tasks_html += `
            <div class="p-4 border rounded-md shadow-md w-full flex justify-between items-center">
              <div id="${task.id}" class="flex flex-col">
                  <h2 id="${task.id}-name" class="text-lg text-neutral-950">${task.name}</h2>
                  Status: <span id="${task.id}-status" class="text-sm text-neutral-500">${task.status}</span>
                  <br>
                  Descrição: <span id="${task.id}-description" class="text-sm text-neutral-500">${task.description}</span>
                </div>
                  <div class="flex items-center gap-2">
                    <button class="bg-primary text-white rounded-md px-3 py-1 update-task-btn" data-bs-toggle="modal" data-bs-target="#updateTaskModal" data-id="${task.id}"">Alterar</button>
                    <button class="bg-primary text-white rounded-md px-3 py-1" onclick="update_status('${task.id}')">Alterar Status</button>
                    <button class="h-[30px] w-[30px] bg-red-500 text-white rounded-md flex justify-center items-center" onclick="delete_task('${task.id}')">
                      <span class="material-symbols-outlined">delete</span>
                    </button>
                  </div>
                </div>
              </div>`
          })
          document.getElementById('tasks-container').innerHTML = tasks_html;

          const updateButtons = document.querySelectorAll('.update-task-btn');

          updateButtons.forEach(button => {
            button.addEventListener('click', function() {
              task_id = this.getAttribute('data-id')
              const task_name = document.getElementById(`${task_id}-name`).innerText;
              const task_description = document.getElementById(`${task_id}-description`).innerText;
              document.getElementById('update-name').value = task_name;
              document.getElementById('update-description').value = task_description;
            });
          });
        } else if(this.status == 401) {
          alert('Sessão expirada');
          sessionStorage.removeItem('auth_token');
          sessionStorage.removeItem('user_id');
          window.location.href = 'index.html';
        }else {
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
    }

    
  } catch (error) {
    console.error(error);
    alert('Erro ao carregar tarefas');
  }
}


const create_task = () => {
  try {
    let task_name = document.getElementById('name').value;
    let task_description = document.getElementById('description').value;

    if (task_name == "" || task_description == "") {
      alert('Preencha todos os campos');
      return;
    }

    let xhttp = new XMLHttpRequest();
    let user_id = sessionStorage.getItem('user_id');

    xhttp.open("POST", server_url + '/task', true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.setRequestHeader("Authorization", "Bearer " + auth_token);

    xhttp.send(JSON.stringify({
      user_id: user_id,
      name: task_name,
      description: task_description
    }));

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 201) {
          alert('Tarefa criada com sucesso');
          window.location.reload();
        } else {
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
    alert('Erro ao criar tarefa');
  }
}

const update_task = () => {
  try {
    let task_name = document.getElementById('update-name').value;
    let task_description = document.getElementById('update-description').value;

    if (task_name == "" || task_description == "") {
      alert('Preencha todos os campos');
      return;
    }

    let xhttp = new XMLHttpRequest();

    xhttp.open("PUT", server_url + '/task/' + task_id, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.setRequestHeader("Authorization", "Bearer " + auth_token);

    xhttp.send(JSON.stringify({
      name: task_name,
      description: task_description
    }));

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4) {
        if (this.status == 200) {
          alert('Tarefa atualizada com sucesso');
          window.location.reload();
        } else {
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
    alert('Erro ao criar tarefa');
  }
}
  
document.getElementById('create-task-btn').addEventListener('click', create_task);
document.getElementById('update-task-btn').addEventListener('click', update_task);