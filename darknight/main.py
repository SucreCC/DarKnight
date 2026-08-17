import sys
from pathlib import Path

# Direct execution adds ``darknight/`` to sys.path[0], which shadows stdlib ``logging``.
_project_root = Path(__file__).resolve().parents[1]
_script_dir = Path(__file__).resolve().parent
if sys.path and Path(sys.path[0]).resolve() == _script_dir:
    sys.path.pop(0)
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import asyncio
import logging
import os
import ssl
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import click
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# Force unbuffered output
os.environ["PYTHONUNBUFFERED"] = "1"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True, encoding="utf-8", errors="replace")


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


def build_bind_args(app_config, logger: logging.Logger) -> dict:
    server = app_config.server
    ssl_config = server.ssl
    debug = app_config.web.debug
    project_name = app_config.project.project_name
    bind_args: dict = {}

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
            logger.warning(
                f"""
{click.style("IMPORTANT!", blink=True, bold=True, fg="yellow")}
You're running {project_name} without specifying {click.style("server.ssl.certfile", italic=True, fg="magenta")} and {click.style("server.ssl.keyfile", italic=True, fg="magenta")}.
The application will only be accessible through localhost. This means that {click.style(f"{project_name} and subscription URLs will not be accessible externally", bold=True)}.

If you need external access, please provide the SSL files to allow the server to bind to 0.0.0.0. Alternatively, you can run the server on localhost or a Unix socket and use a reverse proxy, such as Nginx or Caddy, to handle SSL termination and provide external access.

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


def main() -> None:
    from darknight.api.v1.api_worker import APIWorker
    from darknight.logging import configure_logging
    from darknight.services.config.settings import get_app_config

    configure_logging()
    app_config = get_app_config()

    logger = logging.getLogger(f"{app_config.logging.namespace}.main")
    debug = app_config.web.debug
    bind_args = build_bind_args(app_config, logger)

    log_level_name = app_config.logging.level
    uvicorn_log_level = logging.DEBUG if debug else getattr(logging, log_level_name, logging.INFO)

    # Do NOT change workers count for now
    # multi-workers support isn't implemented yet for APScheduler and XRay module
    worker = APIWorker(app_config)
    worker.run(
        bind_args,
        reload=debug,
        log_level=uvicorn_log_level,
    )


if __name__ == "__main__":
    main()
