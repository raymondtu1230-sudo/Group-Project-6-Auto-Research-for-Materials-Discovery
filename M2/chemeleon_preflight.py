"""M2 task-specific adapter for the unchanged legacy cloud transport."""
try:
    from .frozen_routing import active, fingerprint, main
except ImportError:
    from frozen_routing import active, fingerprint, main

if __name__ == "__main__":
    if not active():
        raise SystemExit("This controller admits only the explicit frozen routing-off task")
    main("preflight")
