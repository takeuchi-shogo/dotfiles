"""Allow running as: python -m project_context"""

from .server import mcp


def main():
    mcp.run()


if __name__ == "__main__":
    main()
