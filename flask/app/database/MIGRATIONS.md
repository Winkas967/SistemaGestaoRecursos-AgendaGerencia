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
