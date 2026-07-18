"""Ensures only one MuslimDesk instance runs at a time. A second launch
signals the first (via a local named-pipe server) to raise its window, then
exits immediately -- otherwise two full instances would each run their own
azan scheduler and race to write the same settings/data files."""
from __future__ import annotations

from PySide6.QtNetwork import QLocalServer, QLocalSocket

_SERVER_NAME = "MuslimDeskInstance"


def try_signal_existing_instance() -> bool:
    """Returns True if another instance is already running (and has just
    been signaled to show its window)."""
    socket = QLocalSocket()
    socket.connectToServer(_SERVER_NAME)
    if socket.waitForConnected(200):
        socket.write(b"show")
        socket.waitForBytesWritten(200)
        socket.disconnectFromServer()
        return True
    return False


def start_server(on_show_requested) -> QLocalServer:
    """Starts listening for future launches. Must be kept alive (assigned to
    a variable) for the lifetime of the app, or it will be garbage collected
    and stop listening."""
    QLocalServer.removeServer(_SERVER_NAME)  # clears a stale socket left by a crashed previous run
    server = QLocalServer()
    server.listen(_SERVER_NAME)

    def _handle_new_connection() -> None:
        sock = server.nextPendingConnection()
        if sock is None:
            return
        sock.readyRead.connect(lambda: (sock.readAll(), on_show_requested()))
        sock.disconnected.connect(sock.deleteLater)

    server.newConnection.connect(_handle_new_connection)
    return server
