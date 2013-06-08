; Original by Andrew Redd 2011 <halpo@users.sourceforge.net>
; Modified by Randy Lai 2013 <randy.cs.lai@gmail.com>
; use govorned by the MIT license http://www.opensource.org/licenses/mit-license.php


RGetOrStart()
{
    Outputdebug % dstring . "entering"
    SetTitleMatchMode, 3
    SetTitleMatchMode, Fast
    global x64

    if (WinExist("Rterm (32-bit)") and x64=0)
    {
        Outputdebug % dstring . "found  term"
        ;WinActivate ; ahk_class RGui
        WinGet RprocID, ID ;,A
        Outputdebug % dstring . "exiting, RprocID=" . RprocID
        return RprocID
    }
    else if (WinExist("Rterm (64-bit)") and x64=1)
    {
        Outputdebug % dstring . " found Rterm (64-bit)"
        ;WinActivate ; ahk_class RGui
        WinGet RprocID, ID ;,A
        outputdebug % dstring . "exiting RprocID=" . RprocID
        return RprocID
    }
    else
    {
        SetTitleMatchMode, 1
        Outputdebug % dstring . "R not found"
        global Rtermexe
        ;setworkingdir %dir%
        ;EnvSet , R_ENVIRON_USER, %scriptdir%
        run %Rtermexe% --sdi,dir,,RprocID
        WinWait ,Rterm,, 2
        WinGet RprocID, ID ,A
        Outputdebug % dstring . "Exiting, RprocID=" . RprocID
        return RprocID
    }
}


Rpaste:
{
    oldclipboard = %clipboard%

    if 0=2
    {
        ;Rtermexe =  "C:\Program Files\R\R-3.0.1\bin\i386\Rgui.exe"
        ;Rtermexe = "C:\Program Files\R\R-3.0.1\bin\x64\Rgui.exe"
        Rtermexe = %1%
        if (Rtermexe = 1)
        {
            RegRead, Rhome, HKEY_LOCAL_MACHINE,SOFTWARE\R-core\R64, InstallPath
            OutputDebug Rhome from registry is %Rhome%
            Rtermexe := Rhome . "\bin\x64\Rterm.exe"
        }
        else if (Rtermexe = 0){
            RegRead, Rhome, HKEY_LOCAL_MACHINE,SOFTWARE\R-core\R, InstallPath
            OutputDebug Rhome from registry is %Rhome%
            Rtermexe := Rhome . "\bin\i386\Rterm.exe"
        }
        cmd = %2%
        cmd := RegExReplace(cmd, "^\n", "")
        newline = `n
        clipboard := cmd . newline
        x64 := Instr(Rtermexe, "x64")>0
    }
    else
    {
        ; for debug
        RegRead, Rhome, HKEY_LOCAL_MACHINE,SOFTWARE\R-core\R64, InstallPath
        OutputDebug Rhome from registry is %Rhome%
        Rtermexe := Rhome . "\bin\x64\Rterm.exe"
        clipboard = proc.time()`n
        x64 := Instr(Rtermexe, "x64")>0
    }
    OutputDebug x64 is %x64%
    OutputDebug  Get current Window
    WinGet stID, ID, A          ; save current window ID to return here later


    RprocID:=RGetOrStart()
    WinActivate ahk_id %RprocID%
    ;WinMenuSelectItem ahk_id %RprocID%,,Edit,Paste ;edit->paste
    ;Send %Clipboard%

    SendInput {Raw}%clipboard%
    ;ControlSendRaw, , %clipboard% , ahk_id %RprocID%

    ; finalize
    WinActivate ahk_id %stID%
    clipboard := oldclipboard
}
;ListVars
;pause
;return