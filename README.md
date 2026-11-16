# TicketDesk — интерактивная документация

Практическое занятие № 6 (МДК.04.01). Комплект документации в Markdown для консольной системы учёта заявок **TicketDesk**.

**Начать чтение:** [index.md](index.md)

## Структура проекта

```text
interactive-documentation/
├── README.md
├── index.md
├── quick-start.md
├── installation.md
├── user-guide.md
├── reference.md
├── faq.md
├── troubleshooting.md
├── mkdocs.yml
├── app/ticketdesk.py      # документируемая программа
└── images/                # scheme.svg, lifecycle.svg, interface.svg
```

## Просмотр

- **GitHub/GitLab:** загрузите папку в репозиторий, Markdown-файлы и SVG отображаются автоматически.
- **VS Code:** откройте папку, нажмите `Ctrl+Shift+V` для предпросмотра.
- **MkDocs:** `pip install mkdocs`, затем `mkdocs serve` (сайт на http://127.0.0.1:8000).
