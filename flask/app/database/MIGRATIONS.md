# Migrações do banco de dados

Execute os arquivos abaixo no banco de produção, nesta ordem:

1. `schema.sql` — somente quando o banco estiver sendo criado do zero.
2. `seeds.sql` — cadastra roles, módulos, categorias e tipos básicos.
3. `migrations/20260825_email_notifications.sql` — configuração dos avisos por e-mail.
4. `migrations/20260903_evaluations.sql` — avaliações, termo de adesão e ano de referência.
5. `checklists.sql` — tabelas, modelos, vínculos, seções e 124 perguntas dos checklists.
6. `migrations/20260904_multiple_checklists_feedback.sql` — permite vários checklists por avaliação e um feedback independente para cada checklist.
7. `migrations/20260904_feedback_documents_email.sql` — adiciona a classificação, os PDFs e o histórico de envio dos feedbacks.

Antes de aplicar em produção, faça backup do banco e execute os arquivos usando o banco correto. A migração 7 deve ser executada somente uma vez em cada banco.

8. `migrations/20260908_checklist_nome.sql` — adiciona o nome do checklist (usado para identificar cada checklist nas telas de avaliação).
9. `migrations/20260910_checklist_teve_visita.sql` — adiciona o indicador de "teve visita ou não" ao checklist.
10. `migrations/20260916_configuracoes_sistema.sql` — cria a tabela de configurações gerais do sistema (usada pelo botão de avisos por e-mail da documentação) e o registro padrão, começando desligado.
11. `migrations/20260918_checklist_encerramento_sem_visita.sql` — registra o novo status "sem_visita" das avaliações (botão "Encerrar atendimento" no checklist). Não altera a estrutura do banco, apenas documenta a mudança.
12. `migrations/20260918_termo_atendimento_centro_medico.sql` — registra a nova opção "Atendimento Centro médico/EVB" do termo de adesão (documento obrigatório, encerra a avaliação definitivamente). Não altera a estrutura do banco, apenas documenta a mudança.
13. `migrations/20261007_checklist_modelo_anos.sql` — cria a tabela `checklist_modelo_anos`, que passa a decidir, por categoria + ano de referência, qual modelo de checklist está em vigor (tela "Configurar checklists" dentro de Avaliações). Faz o backfill automático: publica, para cada categoria que já tinha um modelo vinculado, esse mesmo modelo em todos os anos que já têm avaliação e no ano corrente — nada quebra em categorias/anos já existentes. Anos futuros que ainda não tiverem configuração feita na tela ficam bloqueados para criação de novo checklist até alguém configurar e publicar as perguntas daquele ano.
