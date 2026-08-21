"""Uvicorn bind and SSL helpers derived from application config."""

from __future__ import annotations

import logging
import os
import ssl
from typing import Any

import click
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from darknight.services.config.models import AppConfig


def validate_cert_and_key(
    cert_file_path: str,
    key_file_path: str,
    ca_type: str,
    logger: logging.Logger,
) -> None:
    if ca_type == "private":
        logger.warning(
            f"""
{click.style("IMPORTANT!", blink=True, bold=True, fg="yellow")}
You're running with: {click.style("server.ssl.ca_type", italic=True, fg="magenta")}: {click.style(f"{ca_type}", bold=True, fg="yellow")}.
Self-signed CAs are useful in testing or internal use cases, they're not suitable for secure public internet communications.
        """
        )
        return

    if not os.path.isfile(cert_file_path):
        raise ValueError(f"SSL certificate file '{cert_file_path}' does not exist.")
    if not os.path.isfile(key_file_path):
        raise ValueError(f"SSL key file '{key_file_path}' does not exist.")

    try:
        context = ssl.create_default_context()
        context.load_cert_chain(certfile=cert_file_path, keyfile=key_file_path)
    except ssl.SSLError as e:
        raise ValueError(f"SSL Error: {e}") from e

    try:
        with open(cert_file_path, "rb") as cert_file:
            cert_data = cert_file.read()
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        if cert.issuer == cert.subject:
            raise ValueError("The certificate is self-signed and not issued by a trusted CA.")

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Certificate verification failed: {e}") from e


def build_bind_args(app_config: AppConfig, logger: logging.Logger) -> dict[str, Any]:
    server = app_config.server
    ssl_config = server.ssl
    debug = app_config.web.debug
    project_name = app_config.project.project_name
    bind_args: dict[str, Any] = {}

    if ssl_config.certfile and ssl_config.keyfile and ssl_config.ca_type:
        validate_cert_and_key(
            ssl_config.certfile,
            ssl_config.keyfile,
            ssl_config.ca_type,
            logger,
        )

        bind_args["ssl_certfile"] = ssl_config.certfile
        bind_args["ssl_keyfile"] = ssl_config.keyfile

        if server.uds:
            bind_args["uds"] = server.uds
        else:
            bind_args["host"] = server.host
            bind_args["port"] = server.port
    else:
        if server.uds:
            bind_args["uds"] = server.uds
        else:
            env_host = os.environ.get("UVICORN_HOST")
            env_port = os.environ.get("UVICORN_PORT")
            if env_host:
                bind_args["host"] = env_host
                bind_args["port"] = int(env_port) if env_port else server.port
                logger.warning(
                    f"{project_name} is binding to {bind_args['host']}:{bind_args['port']} "
                    "without TLS (UVICORN_HOST). Use a reverse proxy with HTTPS in production."
                )
            else:
                logger.warning(
                    f"""
{click.style("IMPORTANT!", blink=True, bold=True, fg="yellow")}
You're running {project_name} without specifying {click.style("server.ssl.certfile", italic=True, fg="magenta")} and {click.style("server.ssl.keyfile", italic=True, fg="magenta")}.
The application will only be accessible through localhost. This means that {click.style(f"{project_name} and subscription URLs will not be accessible externally", bold=True)}.

If you need external access, please provide the SSL files to allow the server to bind to 0.0.0.0. Alternatively, you can run the server on localhost or a Unix socket and use a reverse proxy, such as Nginx or Caddy, to handle SSL termination and provide external access.

For Docker or reverse-proxy deployments, set {click.style("UVICORN_HOST=0.0.0.0", italic=True, fg="cyan")} to listen on all interfaces over plain HTTP.

If you wish to continue without SSL, you can use SSH port forwarding to access the application from your machine. Note that in this case, subscription functionality will not work.

Use the following command:

{click.style(f"ssh -L {server.port}:localhost:{server.port} user@server", italic=True, fg="cyan")}

Then, navigate to {click.style(f"http://127.0.0.1:{server.port}", bold=True)} on your computer.
                    """
                )

                bind_args["host"] = "127.0.0.1"
                bind_args["port"] = server.port

    if debug:
        bind_args["uds"] = None
        bind_args["host"] = "0.0.0.0"

    return bind_args


def resolve_uvicorn_log_level(app_config: AppConfig) -> int | str:
    if app_config.web.debug:
        return logging.DEBUG

    log_level_name = app_config.logging.level
    return getattr(logging, log_level_name, logging.INFO)


__all__ = [
    "build_bind_args",
    "resolve_uvicorn_log_level",
    "validate_cert_and_key",
]
