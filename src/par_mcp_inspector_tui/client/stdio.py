"""STDIO MCP client implementation."""

import asyncio
import os

from .base import MCPClient, MCPClientError


class StdioMCPClient(MCPClient):
    """MCP client using STDIO transport."""

    def __init__(self, debug: bool = False, roots: list[str] | None = None) -> None:
        """Initialize STDIO client."""
        super().__init__(debug=debug, roots=roots)
        self._process: asyncio.subprocess.Process | None = None
        self._read_task: asyncio.Task[None] | None = None

    async def connect(self, command: str, args: list[str] | None = None, env: dict[str, str] | None = None) -> None:
        """Connect to MCP server via STDIO.

        Args:
            command: Command to execute
            args: Command arguments
            env: Environment variables
        """
        if self._connected:
            raise MCPClientError("Already connected")

        # Prepare environment
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        # Start subprocess
        try:
            self._process = await asyncio.create_subprocess_exec(
                command,
                *(args or []),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=process_env,
            )

            if not self._process.stdin or not self._process.stdout:
                raise MCPClientError("Failed to create subprocess pipes")

            self._connected = True

            # Start reading task
            self._read_task = asyncio.create_task(self._read_loop())

        except Exception as e:
            raise MCPClientError(f"Failed to start process: {e}")

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

        # Terminate process
        if self._process:
            try:
                self._process.terminate()
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except TimeoutError:
                self._process.kill()
                await self._process.wait()
            finally:
                self._process = None

    async def _send_data(self, data: str) -> None:
        """Send data to server via stdin."""
        if not self._process or not self._process.stdin:
            raise MCPClientError("Not connected")

        try:
            self._process.stdin.write(data.encode("utf-8"))
            await self._process.stdin.drain()
        except Exception as e:
            raise MCPClientError(f"Failed to send data: {e}")

    async def _receive_data(self) -> str | None:
        """Receive data from server via stdout."""
        if not self._process or not self._process.stdout:
            raise MCPClientError("Not connected")

        try:
            line = await self._process.stdout.readline()
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
                    # Process ended
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

    def __del__(self) -> None:
        """Cleanup on deletion."""
        if self._process and self._process.returncode is None:
            try:
                self._process.kill()
            except Exception:
                pass
