#!/usr/bin/env python3
"""
Rofi sway window switcher mode (python version) v1.3.
Allows selecting windows to focus and/or close from within Rofi.
Requires i3ipc-python library.
"""
import os
import sys
from time import monotonic, sleep
from i3ipc import Connection

try:
    i3 = Connection()
except ConnectionError as e:
    print(f"Error connecting to Sway via i3ipc: {e}")
    sys.exit(1)

def _iter_all_windows(root):
    """Iterate through all windows"""
    stack = [root]
    while stack:
        con = stack.pop()
        all_nodes = list(con.nodes) + list(con.floating_nodes)
        for _node in reversed(all_nodes):
            stack.append(_node)
        if con is root:
            continue
        if con.name and con.type in ('con', 'floating_con'):
            yield con

def _get_icon(app_id: str) -> str:
    """Get the icon name for an application, manipulate string if needed"""
    if app_id.startswith(('org.', 'dev.')):
        return app_id
    if app_id == 'signal':
        return f"{app_id}-desktop"
    return app_id.lower()

def _format_workspace(wsid: str) -> str:
    """Format workspace name for display"""
    if wsid == '__i3_scratch':
        return '[-]'
    if not wsid.isdigit():
        return f"[{wsid.split('<span', 1)[0]} ]"
    return f"[{wsid}]"

def _get_windows() -> None:
    """Get list of all windows to display"""
    tree = i3.get_tree()
    scratch_count = 0
    window_list = []
    for con in _iter_all_windows(tree):
        win_id = con.id
        urgent = 'true' if con.urgent else 'false'
        active = 'true' if con.focused else 'false'
        ws = con.workspace()
        wsid = ws.name if ws else 'unknown'
        app_id = con.app_id or con.window_class or 'unknown'
        title = con.name
        icon = _get_icon(app_id)
        ws_display = _format_workspace(wsid)
        if wsid == '__i3_scratch':
            scratch_count += 1
        output_line = (
            f"{ws_display} {app_id}: {title}\0icon\x1f{icon}\x1finfo"
            f"\x1f{win_id}\x1furgent\x1f{urgent}\x1factive\x1f{active}"
        )
        window_list.append(output_line)
    if window_list:
        print('\n'.join(window_list))
    if scratch_count >= 2: # No need to allow presenting/closing all if n < 2
        print("[ALL SCRATCHPAD WINDOWS]")

def _window_exists(tree, win_id: int) -> bool:
    """Check if window is still in tree"""
    return tree.find_by_id(win_id) is not None

def _wait_for_windows_to_disappear(win_ids: list[int], timeout: float = 1.0) -> None:
    """Wait for specified window(s) to disappear with timeout"""
    deadline = monotonic() + timeout
    remaining = set(win_ids)
    while remaining and monotonic() < deadline:
        tree = i3.get_tree()
        remaining = {win_id for win_id in remaining if _window_exists(tree, win_id)}
        if remaining:
            sleep(0.02) # Reasonable poll interval for responsiveness/cpu?

def _kill_scratched() -> None:
    """Close all scratchpad windows"""
    tree = i3.get_tree()
    scratch_ids = [con.id for con in tree.scratchpad()]
    for win_id in scratch_ids:
        i3.command(f"[con_id={win_id}] kill")
    _wait_for_windows_to_disappear([int(win_id) for win_id in scratch_ids])

def main():
    """Get window list, handle scratchpad, present or close windows"""
    rofi_retv = os.environ.get('ROFI_RETV', '0')
    rofi_info = os.environ.get('ROFI_INFO', '')
    selection = sys.argv[1] if len(sys.argv) > 1 else ""
    if rofi_retv == '0':
        _get_windows()
        sys.exit(0)
    elif rofi_retv == '1':
        if selection == "[ALL SCRATCHPAD WINDOWS]":
            i3.command("[floating] scratchpad show")
        else:
            if rofi_info:
                i3.command(f"[con_id={rofi_info}] focus")
        sys.exit(0)
    elif rofi_retv == '3':
        if selection == "[ALL SCRATCHPAD WINDOWS]":
            _kill_scratched()
            _get_windows()
        else:
            if rofi_info:
                i3.command(f"[con_id={rofi_info}] kill")
                _wait_for_windows_to_disappear([int(rofi_info)])
                _get_windows()
        sys.exit(0)

if __name__ == "__main__":
    main()
