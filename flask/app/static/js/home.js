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

// ---------- Busca na tabela de agendamentos ----------

const pesquisa = document.getElementById("pesquisa");

if (pesquisa) {
    pesquisa.addEventListener("keyup", function () {
        const texto = this.value.toLowerCase();
        const linhas = document.querySelectorAll(".linha-agendamento");

        linhas.forEach(function (linha) {
            const conteudo = linha.innerText.toLowerCase();
            linha.style.display = conteudo.includes(texto) ? "" : "none";
        });
    });
}

// ---------- Troca de abas (Meus Agendamentos / Em Aberto) ----------

const tabButtons = document.querySelectorAll(".tab-btn");
const tabPanels = {
    agendamentos: document.getElementById("panel-agendamentos"),
    aberto: document.getElementById("panel-aberto"),
    usuarios: document.getElementById("panel-usuarios"),
};

function ativarAba(nome, centralizar = false) {
    tabButtons.forEach((btn) => {
        const isActive = btn.dataset.tab === nome;
        btn.classList.toggle("active", isActive);
        btn.setAttribute("aria-selected", isActive ? "true" : "false");
    });

    Object.entries(tabPanels).forEach(([key, painel]) => {
        if (!painel) return;
        painel.classList.toggle("active", key === nome);
    });

    sessionStorage.setItem("abaAtiva", nome);

    if (centralizar && tabPanels[nome]) {
        window.requestAnimationFrame(() => {
            tabPanels[nome].scrollIntoView({
                behavior: "smooth",
                block: "center",
            });
        });
    }
}

tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => ativarAba(btn.dataset.tab));
});

const params = new URLSearchParams(window.location.search);
const abaUrl = params.get("tab");
const abaSalva = abaUrl || sessionStorage.getItem("abaAtiva");

if (abaSalva && tabPanels[abaSalva]) {
    ativarAba(abaSalva, Boolean(abaUrl));
}

// ---------- Usuarios / redefinicao de senha ----------

const pesquisaUsuarios = document.getElementById("pesquisaUsuarios");

if (pesquisaUsuarios) {
    pesquisaUsuarios.addEventListener("keyup", function () {
        const texto = this.value.toLowerCase();
        const linhas = document.querySelectorAll(".linha-usuario");

        linhas.forEach((linha) => {
            const conteudo = `${linha.dataset.usuario} ${linha.dataset.role} ${linha.dataset.email || ""}`.toLowerCase();
            linha.style.display = conteudo.includes(texto) ? "" : "none";
        });
    });
}

const passwordModal = document.getElementById("passwordModal");
const passwordModalClose = document.getElementById("passwordModalClose");
const passwordModalCancel = document.getElementById("passwordModalCancel");
const modalUsuarioId = document.getElementById("modalUsuarioId");
const modalUsuarioNome = document.getElementById("modalUsuarioNome");
const modalSenha = document.getElementById("modalSenha");

function abrirModalSenha(id, nome) {
    if (!passwordModal) return;

    modalUsuarioId.value = id;
    modalUsuarioNome.textContent = nome;
    modalSenha.value = "";
    passwordModal.classList.remove("hidden");
    passwordModal.setAttribute("aria-hidden", "false");
    modalSenha.focus();
}

function fecharModalSenha() {
    if (!passwordModal) return;

    passwordModal.classList.add("hidden");
    passwordModal.setAttribute("aria-hidden", "true");
}

document.querySelectorAll(".reset-password-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        abrirModalSenha(btn.dataset.userId, btn.dataset.userName);
    });
});

[passwordModalClose, passwordModalCancel].forEach((btn) => {
    if (btn) btn.addEventListener("click", fecharModalSenha);
});

if (passwordModal) {
    passwordModal.addEventListener("click", (event) => {
        if (event.target === passwordModal) fecharModalSenha();
    });
}

const selfPasswordModal = document.getElementById("selfPasswordModal");
const selfPasswordModalClose = document.getElementById("selfPasswordModalClose");
const selfPasswordModalCancel = document.getElementById("selfPasswordModalCancel");
const selfPasswordForm = document.getElementById("selfPasswordForm");
const selfNovaSenha = document.getElementById("selfNovaSenha");
const selfConfirmarSenha = document.getElementById("selfConfirmarSenha");

function abrirModalMinhaSenha() {
    if (!selfPasswordModal) return;

    if (selfPasswordForm) selfPasswordForm.reset();
    if (selfConfirmarSenha) selfConfirmarSenha.setCustomValidity("");
    selfPasswordModal.classList.remove("hidden");
    selfPasswordModal.setAttribute("aria-hidden", "false");
    if (selfNovaSenha) selfNovaSenha.focus();
}

function fecharModalMinhaSenha() {
    if (!selfPasswordModal) return;

    selfPasswordModal.classList.add("hidden");
    selfPasswordModal.setAttribute("aria-hidden", "true");
}

document.querySelectorAll("[data-open-self-password]").forEach((btn) => {
    btn.addEventListener("click", abrirModalMinhaSenha);
});

[selfPasswordModalClose, selfPasswordModalCancel].forEach((btn) => {
    if (btn) btn.addEventListener("click", fecharModalMinhaSenha);
});

if (selfPasswordModal) {
    selfPasswordModal.addEventListener("click", (event) => {
        if (event.target === selfPasswordModal) fecharModalMinhaSenha();
    });
}

if (selfConfirmarSenha) {
    selfConfirmarSenha.addEventListener("input", () => {
        selfConfirmarSenha.setCustomValidity("");
    });
}

if (selfPasswordForm) {
    selfPasswordForm.addEventListener("submit", (event) => {
        if (!selfNovaSenha || !selfConfirmarSenha) return;

        if (selfNovaSenha.value !== selfConfirmarSenha.value) {
            event.preventDefault();
            selfConfirmarSenha.setCustomValidity("As senhas nao conferem.");
            selfConfirmarSenha.reportValidity();
            return;
        }

        selfConfirmarSenha.setCustomValidity("");
    });
}

// ---------- Lembrete de devolucao ----------

const reminder = document.getElementById("devolucaoReminder");

function verificarDevolucoes() {
    if (!reminder) return;

    const agora = new Date();
    const linhas = document.querySelectorAll(".linha-agendamento[data-devolucao]");
    let precisaLembrar = false;

    linhas.forEach((linha) => {
        const status = linha.dataset.status;
        const devolucao = linha.dataset.devolucao;

        if (!devolucao || status === "devolvido" || status === "cancelado") return;

        const limite = new Date(devolucao);

        if (agora >= limite) {
            precisaLembrar = true;
        }
    });

    reminder.classList.toggle("hidden", !precisaLembrar);
}

verificarDevolucoes();
setInterval(verificarDevolucoes, 60000);

// ---------- Avatar do usuario ----------

const userPanel = document.querySelector(".user-panel");
const userAvatar = document.querySelector(".user-avatar");

function hashTexto(texto) {
    return [...texto].reduce((acc, char) => {
        return (acc * 31 + char.charCodeAt(0)) >>> 0;
    }, 7);
}

function criarAvatar(nome) {
    const hash = hashTexto(nome || "usuario");
    const peles = ["#f2c7a5", "#d89b73", "#b8734f", "#8f5d43", "#f0b98f"];
    const cabelos = ["#2c221f", "#5a3825", "#1f2933", "#7a4a24", "#111827"];
    const roupas = ["#00995c", "#2563eb", "#c2410c", "#7c3aed", "#0f766e"];
    const fundos = ["#dff4ea", "#e0f2fe", "#fef3c7", "#ede9fe", "#dcfce7", "#ffe4e6", "#fce7f3", "#ccfbf1"];

    const pele = peles[hash % peles.length];
    const cabelo = cabelos[(hash >> 3) % cabelos.length];
    const roupa = roupas[(hash >> 6) % roupas.length];
    const fundo = fundos[(hash >> 9) % fundos.length];
    const sorriso = hash % 2 === 0
        ? '<path d="M23 35c3 3 9 3 12 0" fill="none" stroke="#553226" stroke-width="2" stroke-linecap="round"/>'
        : '<path d="M24 35c2 2 8 2 10 0" fill="none" stroke="#553226" stroke-width="2" stroke-linecap="round"/>';
    const cabeloForma = hash % 3 === 0
        ? `<path d="M15 25c2-12 24-14 30 0-5-7-22-6-30 0z" fill="${cabelo}"/>`
        : hash % 3 === 1
            ? `<path d="M14 27c1-15 27-15 31 0-8-4-22-5-31 0z" fill="${cabelo}"/>`
            : `<path d="M16 21c8-10 24-6 28 6-10-5-19-6-28-6z" fill="${cabelo}"/>`;

    return `
        <svg viewBox="0 0 60 60" role="img" aria-label="Avatar do usuario">
            <rect width="60" height="60" rx="30" fill="${fundo}"/>
            <circle cx="30" cy="30" r="28" fill="none" stroke="#ffffff" stroke-width="3"/>
            <path d="M14 58c2-13 30-13 32 0z" fill="${roupa}"/>
            <circle cx="30" cy="29" r="15" fill="${pele}"/>
            ${cabeloForma}
            <circle cx="24" cy="30" r="1.8" fill="#2b211f"/>
            <circle cx="36" cy="30" r="1.8" fill="#2b211f"/>
            ${sorriso}
        </svg>
    `;
}

if (userPanel && userAvatar) {
    userAvatar.innerHTML = criarAvatar(userPanel.dataset.username);
}

// ---------- Atualiza calendario da reserva ----------

const calendarSelect = document.querySelector("[data-calendar-select='true']");

if (calendarSelect) {
    calendarSelect.addEventListener("change", () => {
        if (!calendarSelect.value) return;

        const url = new URL(window.location.href);
        url.pathname = "/reserva";
        url.searchParams.set("recurso_id", calendarSelect.value);
        window.location.href = url.toString();
    });
}
