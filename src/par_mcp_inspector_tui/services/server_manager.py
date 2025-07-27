"""Server configuration management."""

import uuid
from pathlib import Path

import yaml

from ..models import MCPServer, TransportType


class ServerManager:
    """Manager for MCP server configurations."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize server manager.

        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = Path.home() / ".config" / "par-mcp-inspector-tui" / "servers.yaml"

        self.config_path = config_path
        self.servers: dict[str, MCPServer] = {}
        self._ensure_config_dir()
        self.load()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        """Load server configurations from file."""
        if not self.config_path.exists():
            # Create default servers
            self._create_default_servers()
            self.save()
            return

        try:
            with open(self.config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            self.servers = {}

            for server_id, server_data in data.get("servers", {}).items():
                try:
                    # Convert transport string to enum
                    if "transport" in server_data:
                        server_data["transport"] = TransportType(server_data["transport"])

                    server = MCPServer(id=server_id, **server_data)
                    self.servers[server_id] = server
                except Exception as e:
                    print(f"Error loading server {server_id}: {e}")

        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.servers = {}

    def save(self) -> None:
        """Save server configurations to file."""
        data = {"servers": {}}

        for server_id, server in self.servers.items():
            server_dict = server.model_dump(exclude={"state", "info", "error", "last_connected"})
            # Convert transport enum to string
            server_dict["transport"] = server_dict["transport"].value
            # Remove None values
            server_dict = {k: v for k, v in server_dict.items() if v is not None}
            # Remove id from dict (it's the key)
            server_dict.pop("id", None)
            data["servers"][server_id] = server_dict

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=True)
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def _create_default_servers(self) -> None:
        """Create default server configurations."""
        # Example STDIO server
        self.add_server(
            MCPServer(
                id=str(uuid.uuid4()),
                name="Example STDIO Server",
                transport=TransportType.STDIO,
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                env={"NODE_ENV": "production"},
            )
        )

        # Example HTTP server (uncomment and configure when you have an HTTP MCP server)
        # self.add_server(
        #     MCPServer(
        #         id=str(uuid.uuid4()),
        #         name="Example HTTP Server",
        #         transport=TransportType.HTTP,
        #         url="http://localhost:8080/mcp",
        #     )
        # )

        # Everything server - comprehensive example server with all features
        self.add_server(
            MCPServer(
                id="a49a17c3-a91c-4757-8ec8-effa589fffa1",
                name="Everything",
                transport=TransportType.STDIO,
                command="npx",
                args=["-y", "@modelcontextprotocol/server-everything"],
            )
        )

    def add_server(self, server: MCPServer) -> None:
        """Add a server configuration.

        Args:
            server: Server to add
        """
        self.servers[server.id] = server
        self.save()

    def update_server(self, server: MCPServer) -> None:
        """Update a server configuration.

        Args:
            server: Server to update
        """
        if server.id in self.servers:
            self.servers[server.id] = server
            self.save()

    def remove_server(self, server_id: str) -> None:
        """Remove a server configuration.

        Args:
            server_id: ID of server to remove
        """
        if server_id in self.servers:
            del self.servers[server_id]
            self.save()

    def get_server(self, server_id: str) -> MCPServer | None:
        """Get a server by ID.

        Args:
            server_id: Server ID

        Returns:
            Server or None if not found
        """
        return self.servers.get(server_id)

    def list_servers(self) -> list[MCPServer]:
        """List all server configurations.

        Returns:
            List of servers
        """
        return list(self.servers.values())

    def duplicate_server(self, server_id: str, new_name: str | None = None) -> MCPServer | None:
        """Duplicate a server configuration.

        Args:
            server_id: ID of server to duplicate
            new_name: Name for the new server

        Returns:
            New server or None if original not found
        """
        original = self.get_server(server_id)
        if not original:
            return None

        # Create new server with new ID
        new_data = original.model_dump(exclude={"id", "state", "info", "error", "last_connected"})
        new_server = MCPServer(id=str(uuid.uuid4()), name=new_name or f"{original.name} (Copy)", **new_data)

        self.add_server(new_server)
        return new_server
