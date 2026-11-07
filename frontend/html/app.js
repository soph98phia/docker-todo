// Frontend logic: talks to the backend via the Nginx reverse proxy at /api
const API_URL = "/api/todos";

const form = document.getElementById("todo-form");
const input = document.getElementById("todo-input");
const list = document.getElementById("todo-list");
const statusText = document.getElementById("status");

async function request(url, options = {}) {
    const response = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }
    return response.status === 204 ? null : response.json();
}

function renderTodos(todos) {
    list.innerHTML = "";
    for (const todo of todos) {
        const item = document.createElement("li");
        item.className = todo.done ? "done" : "";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = todo.done;
        checkbox.addEventListener("change", () => toggleTodo(todo.id, checkbox.checked));

        const title = document.createElement("span");
        title.textContent = todo.title;

        const deleteButton = document.createElement("button");
        deleteButton.textContent = "✕";
        deleteButton.className = "delete";
        deleteButton.title = "Delete";
        deleteButton.addEventListener("click", () => deleteTodo(todo.id));

        item.append(checkbox, title, deleteButton);
        list.appendChild(item);
    }
    const openCount = todos.filter((t) => !t.done).length;
    statusText.textContent = todos.length ? `${openCount} of ${todos.length} open` : "No tasks yet.";
}

async function loadTodos() {
    try {
        renderTodos(await request(API_URL));
    } catch (error) {
        statusText.textContent = "Could not reach the backend.";
        console.error(error);
    }
}

async function toggleTodo(id, done) {
    await request(`${API_URL}/${id}`, { method: "PATCH", body: JSON.stringify({ done }) });
    loadTodos();
}

async function deleteTodo(id) {
    await request(`${API_URL}/${id}`, { method: "DELETE" });
    loadTodos();
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = input.value.trim();
    if (!title) return;
    await request(API_URL, { method: "POST", body: JSON.stringify({ title }) });
    input.value = "";
    loadTodos();
});

loadTodos();
