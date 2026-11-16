#!/usr/bin/env python3
"""TicketDesk - консольная система учёта заявок (учебный проект)."""
import argparse, csv, json, os, sqlite3, sys
from datetime import datetime

VERSION = "1.0.0"
PRIORITIES = ["low", "normal", "high"]
STATUSES = ["new", "in_progress", "closed"]
DEFAULT_CONFIG = {"db_path": "tickets.db", "default_priority": "normal"}


def load_config(path):
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cfg.update(json.load(f))
    return cfg


def connect(cfg):
    if not os.path.exists(cfg["db_path"]):
        sys.exit("Ошибка: база данных не найдена. Выполните: python ticketdesk.py init")
    db = sqlite3.connect(cfg["db_path"])
    db.row_factory = sqlite3.Row
    return db


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def cmd_init(a, cfg):
    if not os.path.exists(a.config):
        with open(a.config, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        print(f"Создан файл конфигурации: {a.config}")
    db = sqlite3.connect(cfg["db_path"])
    db.execute("""CREATE TABLE IF NOT EXISTS tickets(
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
        author TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL,
        created TEXT NOT NULL, updated TEXT NOT NULL)""")
    db.commit()
    print(f"База данных готова: {cfg['db_path']}")


def cmd_add(a, cfg):
    db = connect(cfg)
    prio = a.priority or cfg["default_priority"]
    cur = db.execute("INSERT INTO tickets(title,author,priority,status,created,updated) VALUES(?,?,?,?,?,?)",
                     (a.title, a.author, prio, "new", now(), now()))
    db.commit()
    print(f"Заявка #{cur.lastrowid} создана (приоритет: {prio}, статус: new)")


def cmd_list(a, cfg):
    db = connect(cfg)
    q, p = "SELECT * FROM tickets WHERE 1=1", []
    if a.status:
        q += " AND status=?"; p.append(a.status)
    if a.priority:
        q += " AND priority=?"; p.append(a.priority)
    rows = db.execute(q + " ORDER BY id", p).fetchall()
    if not rows:
        print("Заявок не найдено."); return
    print(f"{'ID':<4} {'Приоритет':<10} {'Статус':<12} Тема")
    for r in rows:
        print(f"{r['id']:<4} {r['priority']:<10} {r['status']:<12} {r['title']}")


def get(db, tid):
    r = db.execute("SELECT * FROM tickets WHERE id=?", (tid,)).fetchone()
    if not r:
        sys.exit(f"Ошибка: заявка #{tid} не найдена.")
    return r


def cmd_show(a, cfg):
    r = get(connect(cfg), a.id)
    for k in ["id", "title", "author", "priority", "status", "created", "updated"]:
        print(f"{k:<9}: {r[k]}")


def set_status(a, cfg, status):
    db = connect(cfg)
    r = get(db, a.id)
    if r["status"] == "closed":
        sys.exit(f"Ошибка: заявка #{a.id} уже закрыта.")
    db.execute("UPDATE tickets SET status=?, updated=? WHERE id=?", (status, now(), a.id))
    db.commit()
    print(f"Заявка #{a.id}: статус изменён на {status}")


def cmd_stats(a, cfg):
    db = connect(cfg)
    for s in STATUSES:
        n = db.execute("SELECT COUNT(*) FROM tickets WHERE status=?", (s,)).fetchone()[0]
        print(f"{s:<12}: {n}")


def cmd_export(a, cfg):
    db = connect(cfg)
    rows = db.execute("SELECT * FROM tickets ORDER BY id").fetchall()
    with open(a.file, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(rows[0].keys() if rows else ["id"])
        w.writerows([tuple(r) for r in rows])
    print(f"Экспортировано заявок: {len(rows)} -> {a.file}")


def main():
    p = argparse.ArgumentParser(prog="ticketdesk", description="Система учёта заявок TicketDesk")
    p.add_argument("--config", default="ticketdesk.json", help="путь к файлу конфигурации")
    p.add_argument("--version", action="version", version=f"TicketDesk {VERSION}")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="создать конфигурацию и базу данных").set_defaults(f=cmd_init)
    s = sub.add_parser("add", help="создать заявку")
    s.add_argument("title"); s.add_argument("--author", required=True)
    s.add_argument("--priority", choices=PRIORITIES); s.set_defaults(f=cmd_add)
    s = sub.add_parser("list", help="показать заявки")
    s.add_argument("--status", choices=STATUSES); s.add_argument("--priority", choices=PRIORITIES)
    s.set_defaults(f=cmd_list)
    s = sub.add_parser("show", help="показать заявку"); s.add_argument("id", type=int); s.set_defaults(f=cmd_show)
    s = sub.add_parser("take", help="взять заявку в работу"); s.add_argument("id", type=int)
    s.set_defaults(f=lambda a, c: set_status(a, c, "in_progress"))
    s = sub.add_parser("close", help="закрыть заявку"); s.add_argument("id", type=int)
    s.set_defaults(f=lambda a, c: set_status(a, c, "closed"))
    sub.add_parser("stats", help="статистика по статусам").set_defaults(f=cmd_stats)
    s = sub.add_parser("export", help="экспорт в CSV"); s.add_argument("file"); s.set_defaults(f=cmd_export)
    a = p.parse_args()
    a.f(a, load_config(a.config))


if __name__ == "__main__":
    main()
