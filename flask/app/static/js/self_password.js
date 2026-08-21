//controla a alteracao da senha do usuario conectado
const ownPasswordModal = document.getElementById("selfPasswordModal");
const ownPasswordForm = document.getElementById("selfPasswordForm");
const ownPasswordOpenButtons = document.querySelectorAll("[data-open-self-password]");
const ownPasswordCloseButton = document.getElementById("selfPasswordModalClose");
const ownPasswordCancelButton = document.getElementById("selfPasswordModalCancel");
const ownCurrentPassword = document.getElementById("selfSenhaAtual");
const ownNewPassword = document.getElementById("selfNovaSenha");
const ownPasswordConfirmation = document.getElementById("selfConfirmarSenha");

function openOwnPasswordModal() {
    if (!ownPasswordModal || !ownPasswordForm) return;

    ownPasswordForm.reset();
    ownPasswordConfirmation.setCustomValidity("");
    ownPasswordModal.classList.remove("hidden");
    ownPasswordModal.setAttribute("aria-hidden", "false");
    ownCurrentPassword.focus();
}

function closeOwnPasswordModal() {
    if (!ownPasswordModal) return;

    ownPasswordModal.classList.add("hidden");
    ownPasswordModal.setAttribute("aria-hidden", "true");
}

ownPasswordOpenButtons.forEach((button) => {
    button.addEventListener("click", openOwnPasswordModal);
});

[ownPasswordCloseButton, ownPasswordCancelButton].forEach((button) => {
    if (button) button.addEventListener("click", closeOwnPasswordModal);
});

if (ownPasswordModal) {
    ownPasswordModal.addEventListener("click", (event) => {
        if (event.target === ownPasswordModal) closeOwnPasswordModal();
    });
}

if (ownPasswordConfirmation) {
    ownPasswordConfirmation.addEventListener("input", () => {
        ownPasswordConfirmation.setCustomValidity("");
    });
}

if (ownPasswordForm) {
    ownPasswordForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (ownNewPassword.value !== ownPasswordConfirmation.value) {
            ownPasswordConfirmation.setCustomValidity("As senhas não conferem.");
            ownPasswordConfirmation.reportValidity();
            return;
        }

        const submitButton = ownPasswordForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = "Salvando...";

        try {
            const response = await fetch(ownPasswordForm.action, {
                method: ownPasswordForm.dataset.apiMethod,
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    senha_atual: ownCurrentPassword.value,
                    nova_senha: ownNewPassword.value,
                    confirmar_senha: ownPasswordConfirmation.value,
                }),
            });

            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(result.error || "Não foi possível alterar a senha.");
            }

            closeOwnPasswordModal();
            ownPasswordForm.reset();
            window.alert(result.message || "Senha alterada com sucesso.");
        } catch (error) {
            window.alert(error.message);
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = "Salvar senha";
        }
    });
}
