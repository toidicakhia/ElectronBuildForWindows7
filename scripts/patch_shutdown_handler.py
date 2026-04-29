import os
import shutil
import sys


def resolve(*parts: str) -> str:
    return os.path.normpath(os.path.join(*parts))

def rmtree_verbose(path: str) -> None:
    if os.path.exists(path):
        print(f"  Removing : {path}")
        shutil.rmtree(path)
    else:
        print(f"  Not found (skip remove): {path}")

def copytree_verbose(src: str, dst: str) -> None:
    if not os.path.exists(src):
        print(f"  ERROR: source not found: {src}", file=sys.stderr)
        sys.exit(1)
    print(f"  Copying  : {src}")
    print(f"       to  : {dst}")
    shutil.copytree(src, dst)

def patch_shutdown_handler(project_dir: str, handler_src: str) -> None:
    target = resolve(
        project_dir,
        "node_modules",
        "@get-wrecked",
        "electron-shutdown-handler",
        "dist",
    )
    print(f"Patching electron-shutdown-handler dist")
    print(f"  Source: {handler_src}")
    print(f"  Target: {target}")

    if not os.path.exists(handler_src):
        print("  Source not found, skipping.")
        return

    rmtree_verbose(target)

    parent = os.path.dirname(target)
    if not os.path.exists(parent):
        print(f"  Creating parent: {parent}")
        os.makedirs(parent, exist_ok=True)

    copytree_verbose(handler_src, target)
    print("  Done.")

def main() -> None:
    project_dir = resolve(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    handler_src = resolve(os.getcwd(), "sources", "electron-shutdown-handler", "dist")

    print(f"Project dir          : {project_dir}")
    print(f"Shutdown handler src : {handler_src}")
    print()

    patch_shutdown_handler(project_dir, handler_src)

    print("\nDone.")


if __name__ == "__main__":
    main()
