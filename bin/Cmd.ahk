; save current window ID to return here later
WinGet stID, ID, A

; Get Cygwin window
WinGet, cmd_id, ID, ahk_class ConsoleWindowClass

; if not found, open cygwin
if (cmd_id != "")
{
    Outputdebug % dstring . "id=" . cmd_id

    oldclipboard = %clipboard%
    if 0=2
    {
        cmd = %2%
        cmd := RegExReplace(cmd, "^\n", "")
        newline = `n
        clipboard := cmd . newline
    }
    Else
    {
        clipboard = proc.time()`n
    }

    WinActivate ahk_id %cmd_id%
    SendInput {Raw}%clipboard%
    WinActivate ahk_id %stID%
    clipboard := oldclipboard
}
