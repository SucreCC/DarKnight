from darknight.runtime.bootstrap import prepare_process


def main() -> None:
    prepare_process()

    from darknight.api.v1.api_worker import APIWorker
    from darknight.logging import configure_logging

    configure_logging()

    # Do NOT change workers count for now
    # multi-workers support isn't implemented yet for APScheduler and XRay module
    APIWorker().run()


if __name__ == "__main__":
    main()
