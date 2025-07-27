"""TCP MCP client implementation."""

import asyncio

from .base import MCPClient, MCPClientError


class TcpMCPClient(MCPClient):
    """MCP client using TCP transport."""

    def __init__(self, debug: bool = False, roots: list[str] | None = None) -> None:
        """Initialize TCP client."""
        super().__init__(debug=debug, roots=roots)
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._read_task: asyncio.Task[None] | None = None

    async def connect(self, host: str, port: int) -> None:
        """Connect to MCP server via TCP.

        Args:
            host: Server hostname or IP
            port: Server port
        """
        if self._connected:
            raise MCPClientError("Already connected")

        try:
            # Connect to server
            self._reader, self._writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=10.0)

            self._connected = True

            # Start reading task
            self._read_task = asyncio.create_task(self._read_loop())

        except TimeoutError:
            raise MCPClientError(f"Connection timeout to {host}:{port}")
        except Exception as e:
            raise MCPClientError(f"Failed to connect to {host}:{port}: {e}")

    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        if not self._connected:
            return

        self._connected = False

        # Cancel read task
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass

        # Close connection
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
            finally:
                self._writer = None
                self._reader = None

    async def _send_data(self, data: str) -> None:
        """Send data to server via TCP."""
        if not self._writer:
            raise MCPClientError("Not connected")

        try:
            self._writer.write(data.encode("utf-8"))
            await self._writer.drain()
        except Exception as e:
            raise MCPClientError(f"Failed to send data: {e}")

    async def _receive_data(self) -> str | None:
        """Receive data from server via TCP."""
        if not self._reader:
            raise MCPClientError("Not connected")

        try:
            line = await self._reader.readline()
            if not line:
                return None
            return line.decode("utf-8").strip()
        except Exception as e:
            raise MCPClientError(f"Failed to receive data: {e}")

    async def _read_loop(self) -> None:
        """Continuously read from server."""
        while self._connected:
            try:
                data = await self._receive_data()
                if data is None:
                    # Connection closed
                    self._connected = False
                    break

                await self._handle_incoming_data(data)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in read loop: {e}")
                # Continue reading unless disconnected
                if not self._connected:
                    break
