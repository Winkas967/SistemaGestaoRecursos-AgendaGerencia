const root = document.documentElement;
const toggleBtn = document.getElementById("themeToggle");
const iconSun = document.getElementById("iconSun");
const iconMoon = document.getElementById("iconMoon");
const label = document.getElementById("themeLabel");

function applyTheme(theme) {
    root.setAttribute("data-theme", theme);

    if (theme === "dark") {
        iconSun.style.display = "none";
        iconMoon.style.display = "block";
        label.textContent = "Modo claro";
    } else {
        iconSun.style.display = "block";
        iconMoon.style.display = "none";
        label.textContent = "Modo escuro";
    }

    localStorage.setItem("theme", theme);
}

const savedTheme = localStorage.getItem("theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
let currentTheme = savedTheme || (prefersDark ? "dark" : "light");

applyTheme(currentTheme);

window.addEventListener("load", () => {
    root.classList.remove("is-loading");
    root.classList.add("is-ready");
});

toggleBtn.addEventListener("click", () => {
    currentTheme = currentTheme === "light" ? "dark" : "light";
    applyTheme(currentTheme);
});

const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");

//exibe uma mensagem sem alterar o visual da pag
function showLoginMessage(message) {
    loginMessage.textContent = message;
    loginMessage.hidden = false;
}

//envia o login para api nova
loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    loginMessage.hidden = true;

    const submitButton = loginForm.querySelector(
        'button[type="submit"]'
    );

    const username = document.getElementById("usuario").value;
    const password = document.getElementById("senha").value;

    submitButton.disabled = true;
    submitButton.textContent = "Entrando...";

    try {
        const response = await fetch(loginForm.action, { 
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                usuario: username,
                senha: password,
            }),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.error || "Não foi possível realizar o login."
            );
        }

        window.location.href = loginForm.dataset.homeUrl;

    } catch (error) {
        showLoginMessage(error.message);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Entrar";
    }
});

//encerra a sessao e volta para o login
const logoutForm = document.getElementById("logoutForm");

if (logoutForm) {
    logoutForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const response = await fetch(logoutForm.action, {
            method: "POST",
        });

        if(response.ok) {
            window.location.href = logoutForm.dataset.loginUrl;
        }
    })
}

//salva as permissoes de um modulo para o setor
document.querySelectorAll(".sector-permission-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        try {
            await enviarJson(form.action, form.dataset.apiMethod, {
                modulo_id: Number(form.elements.modulo_id.value),
                pode_visualizar: form.elements.pode_visualizar.checked,
                pode_criar: form.elements.pode_criar.checked,
                pode_editar: form.elements.pode_editar.checked,
                pode_excluir: form.elements.pode_excluir.checked,
            });

            window.alert("Permissões atualizadas com sucesso.");
        } catch (error) {
            window.alert(error.message);
        }
    });
});