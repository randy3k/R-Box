SetTitleMatchMode, 2

; Get Rstudio window
WinGet, rstudio_id, ID, ahk_exe rstudio.exe

WinGet stID, ID, A

if (rstudio_id != "")
{
    Outputdebug % dstring . "id=" . rstudio_id

    oldclipboard = %clipboard%
    if 0=1
    {
        cmd = %1%
        cmd := RegExReplace(cmd, "^\n", "")
        clipboard := cmd
    }
    Else
    {
        clipboard = proc.time()`n
    }

    WinActivate, ahk_id %rstudio_id%

    Send, {Blind}^v
    ; ControlSend, , {Blind}^v, ahk_id %rstudio_id%
    GetKeyState, state, Control
    if state = U
    {
        Send, {Enter}
        ; ControlSend, , {Enter}, ahk_id %rstudio_id%
    }
    Else
    {
        Send, {Ctrl Up}{Enter}{Ctrl Down}
        ; ControlSend, , {Ctrl Up}{Enter}{Ctrl Down}, ahk_id %rstudio_id%
    }
    GetKeyState, state, Control
    Outputdebug % dstring . "state=" . state
    WinActivate, ahk_id %stID%
    clipboard := oldclipboard
}
