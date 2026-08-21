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

// ---------- Integracao com as APIs administrativas ----------

// Envia dados em JSON e trata a resposta da API
async function enviarJson(url, method, data = null) {
    const options = {
        method,
        headers: {
            "Content-Type": "application/json",
        },
    };

    if (data !== null) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(result.error || "Não foi possível concluir a operação.");
    }

    return result;
}

// Reabre a aba de usuários depois de uma alteração
function recarregarPainelUsuarios() {
    const url = new URL(window.location.href);
    url.searchParams.set("tab", "usuarios");
    window.location.href = url.toString();
}

// Atualiza a role do usuário
document.querySelectorAll(".role-update-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        try {
            await enviarJson(form.action, form.dataset.apiMethod, {
                role_id: Number(form.elements.role_id.value),
                setor_id: form.elements.setor_id.value || null,
            });
            recarregarPainelUsuarios();
        } catch (error) {
            window.alert(error.message);
        }
    });
});

// Atualiza o e-mail do usuário
document.querySelectorAll(".user-email-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        try {
            await enviarJson(form.action, form.dataset.apiMethod, {
                email: form.elements.email.value,
            });
            recarregarPainelUsuarios();
        } catch (error) {
            window.alert(error.message);
        }
    });
});

// Cadastra um novo setor
const sectorAddForm = document.querySelector(".sector-add-form");

if (sectorAddForm) {
    sectorAddForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        try {
            await enviarJson(sectorAddForm.action, "POST", {
                nome: sectorAddForm.elements.nome.value,
            });
            recarregarPainelUsuarios();
        } catch (error) {
            window.alert(error.message);
        }
    });
}

// Desativa um setor sem apagar seu histórico
document.querySelectorAll("form[data-sector-id]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!window.confirm("Remover este setor?")) return;

        try {
            await enviarJson(form.action, form.dataset.apiMethod);
            recarregarPainelUsuarios();
        } catch (error) {
            window.alert(error.message);
        }
    });
});

// Redefine a senha de outro usuário
const adminPasswordForm = document.querySelector("[data-admin-password-form]");

if (adminPasswordForm) {
    adminPasswordForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const userId = adminPasswordForm.elements.usuario_id.value;
        const baseUrl = adminPasswordForm.action.replace(/\/$/, "");

        try {
            await enviarJson(`${baseUrl}/${userId}/senha`, adminPasswordForm.dataset.apiMethod, {
                senha: adminPasswordForm.elements.senha.value,
            });
            fecharModalSenha();
            window.alert("Senha atualizada com sucesso.");
        } catch (error) {
            window.alert(error.message);
        }
    });
}

//monta os dados de um formulario de recurso
function getResourceFormData(form) {
    return {
        nome: form.elements.nome.value,
        tipo_recurso_id: Number(form.elements.tipo_recurso_id.value),
        status: form.elements.status.value,
        descricao: form.elements.descricao.value,
    };
}

//cadastra um novo recurso
const resourceCreateForm = document.querySelector(
    ".resource-create-form"
);

if (resourceCreateForm) {
    resourceCreateForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        try{
            await enviarJson(
                resourceCreateForm.action,
                resourceCreateForm.dataset.apiMethod,
                getResourceFormData(resourceCreateForm),
            );

            window.location.reload();
        } catch (error) {
            window.alert(error.message);
        }
    });
}

//atualiza os dados de um recurso
document.querySelectorAll(".resource-edit-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        try {
            await enviarJson(
                form.action,
                form.dataset.apiMethod,
                getResourceFormData(form),
            );

            window.location.reload();
        } catch (error) {
            window.alert(error.message);
        }
    });
});

//atualiza somente o status
document.querySelectorAll(".resource-status-form").forEach((form) => {
    form.addEventListener("submit", async (event) =>{
        event.preventDefault()

        try {
            await enviarJson(
                form.action,
                form.dataset.apiMethod,
                {
                    status: form.elements.status.value,
                },
            );

            window.location.reload();
        } catch (error) {
            window.alert(error.message);
        }
    });
});

//desativa um recurso
document.querySelectorAll(".resource-delete-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const confirmed = window.confirm(
            "Excluir este equipamento?"
        );

        if (!confirmed) {
            return;
        }

        try {
            await enviarJson(
                form.action,
                form.dataset.apiMethod,
            );

            window.location.reload();
        } catch (error) {
            window.alert(error.message);
        }
    });
});

//localiza o formulario de reservas
const reservationForm = document.querySelector(".reservation-form")

if (reservationForm) {
    //envia a nova reserva para a api
    reservationForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const resourceId = reservationForm.elements.recurso_id.value;

        const data = {
            recurso_id: Number(resourceId),
            setor_id: reservationForm.elements.setor_id.value,
            data_reserva: reservationForm.elements.data_reserva.value,
            hora_inicio: reservationForm.elements.hora_inicio.value,
            data_volta: reservationForm.elements.data_volta.value,
            hora_fim: reservationForm.elements.hora_fim.value,
            viagem: reservationForm.elements.viagem?.checked || false,
            motivo: reservationForm.elements.motivo.value,
            observacao: reservationForm.elements.observacao.value,
        };

        try {
            await enviarJson(
                reservationForm.action,
                reservationForm.dataset.apiMethod,
                data,
            );

            window.location.href = (
                `/reserva?recurso_id=${resourceId}`
            );
        } catch (error) {
            window.alert(error.message);
        }
    });
}

//salva as permissoes de cada modulo do setor
document.querySelectorAll(".sector-permission-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const data = {
            modulo_id: Number(form.elements.modulo_id.value),
            pode_visualizar: form.elements.pode_visualizar.checked,
            pode_criar: form.elements.pode_criar.checked,
            pode_editar: form.elements.pode_editar.checked,
            pode_excluir: form.elements.pode_excluir.checked,
        };

        try {
            await enviarJson(
                form.action,
                form.dataset.apiMethod,
                data,
            );

            window.alert("Permissões atualizadas com sucesso.");
            window.location.reload();
        } catch (error) {
            window.alert(error.message);
        }
    })
})
