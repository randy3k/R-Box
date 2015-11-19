; Get Cmder window
WinGet, cmder_id, ID, ahk_class VirtualConsoleClass

if (cmder_id != "")
{
    Outputdebug % dstring . "id=" . cmder_id

    oldclipboard = %clipboard%
    if 0=1
    {
        cmd = %1%
        cmd := RegExReplace(cmd, "^\n", "")
        newline = `n
        clipboard := cmd . newline
    }
    Else
    {
        clipboard = proc.time()`n
    }

    ControlSend, VirtualConsoleClass1 ,{Blind}^+v, ahk_id %cmder_id%
    clipboard := oldclipboard
}
