//controla a saida do usuario em todas as paginas
document.querySelectorAll(".logout-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const button = form.querySelector('button[type="submit"]');

        button.disabled = true;
        button.textContent = "Saindo...";

        try {
            const response = await fetch(form.action, {
                method: "POST",
            });

            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(
                    result.error || "Não foi possível sair do sistema."
                );
            }

            window.location.href = form.dataset.loginUrl;
        } catch (error) {
            window.alert(error.message);
            button.disabled = false;
            button.textContent = "Sair";
        }
    });
});
