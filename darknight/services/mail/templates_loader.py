"""Jinja2 template loader for transactional mail."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape


@dataclass(frozen=True)
class RenderedEmail:
    subject: str
    body_text: str
    body_html: str


class MailTemplateLoader:
    def __init__(self, templates_dir: Path | None = None) -> None:
        self.templates_dir = templates_dir or Path(__file__).resolve().parent / "templates"
        self._env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(enabled_extensions=("html",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def ensure_exists(self, template: str) -> None:
        for suffix in (".subject.txt", ".txt", ".html"):
            path = self.templates_dir / f"{template}{suffix}"
            if not path.is_file():
                raise FileNotFoundError(f"Missing mail template: {path.name}")

    def render(self, template: str, context: dict) -> RenderedEmail:
        self.ensure_exists(template)
        try:
            subject = self._env.get_template(f"{template}.subject.txt").render(**context).strip()
            body_text = self._env.get_template(f"{template}.txt").render(**context).strip()
            body_html = self._env.get_template(f"{template}.html").render(**context).strip()
        except TemplateNotFound as exc:
            raise FileNotFoundError(f"Missing mail template: {exc.name}") from exc
        return RenderedEmail(subject=subject, body_text=body_text, body_html=body_html)


__all__ = ["MailTemplateLoader", "RenderedEmail"]
