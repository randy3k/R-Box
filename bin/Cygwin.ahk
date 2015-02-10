; Get Cygwin window
WinGet, cygwin_id, ID, ahk_class mintty

; if not found, open cygwin
if (cygwin_id != "")
{
    Outputdebug % dstring . "id=" . cygwin_id

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

    ControlSend, ,{Blind}{Shift down}{Insert}{Shift Up}, ahk_id %cygwin_id%
    clipboard := oldclipboard
}
