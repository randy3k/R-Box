; Original by Andrew Redd 2011 <halpo@users.sourceforge.net>
; Modified by Randy Lai 2013 <randy.cs.lai@gmail.com>
; use govorned by the MIT license http://www.opensource.org/licenses/mit-license.php


RGetOrStart(Rguiexe, x64) {
    Outputdebug % dstring . "entering"
    SetTitleMatchMode, 3
    SetTitleMatchMode, Fast
    ; global x64

    if (WinExist("R Console (32-bit)") and x64=0) {
        Outputdebug % dstring . "found R Console"
        ;WinActivate ; ahk_class RGui
        WinGet RprocID, ID ;,A
        Outputdebug % dstring . "exiting, RprocID=" . RprocID
        return RprocID
    }
    else if (WinExist("R Console (64-bit)") and x64=1) {
        Outputdebug % dstring . " found R Console (64-bit)"
        ;WinActivate ; ahk_class RGui
        WinGet RprocID, ID ;,A
        outputdebug % dstring . "exiting RprocID=" . RprocID
        return RprocID
    }
    else {
        SetTitleMatchMode, 1
        Outputdebug % dstring . "R not found"
        ;setworkingdir %dir%
        ;EnvSet , R_ENVIRON_USER, %scriptdir%
        run %Rguiexe% --sdi,dir,,RprocID
        WinWait ,R Console,, 2
        WinGet RprocID, ID ,A
        Outputdebug % dstring . "Exiting, RprocID=" . RprocID
        return RprocID
    }
}


oldclipboard = %clipboard%

if 0=2 
{
    ;Rguiexe =  "C:\Program Files\R\R-3.0.1\bin\i386\Rgui.exe"
    ;Rguiexe = "C:\Program Files\R\R-3.0.1\bin\x64\Rgui.exe"
    Rguiexe = %1%
    if (Rguiexe = 1) {
        RegRead, Rhome, HKEY_LOCAL_MACHINE,SOFTWARE\R-core\R, InstallPath
        OutputDebug Rhome from registry is %Rhome%
        Rguiexe := Rhome . "\bin\x64\Rgui.exe"
    }
    else if (Rguiexe = 0){
        RegRead, Rhome, HKEY_LOCAL_MACHINE,SOFTWARE\R-core\R, InstallPath
        OutputDebug Rhome from registry is %Rhome%
        Rguiexe := Rhome . "\bin\i386\Rgui.exe"
    }
    cmd = %2%
    cmd := RegExReplace(cmd, "^\n", "")
    newline = `n
    clipboard := cmd . newline
    x64 := Instr(Rguiexe, "x64")>0
}
else {
    ; for debug
    RegRead, Rhome, HKEY_LOCAL_MACHINE,SOFTWARE\R-core\R64, InstallPath
    OutputDebug Rhome from registry is %Rhome%
    Rguiexe := Rhome . "\bin\x64\Rgui.exe"
    clipboard = proc.time()`n
    x64 := Instr(Rguiexe, "x64")>0
}

OutputDebug x64 is %x64%
OutputDebug  Get current Window
WinGet stID, ID, A          ; save current window ID to return here later

RprocID:=RGetOrStart(Rguiexe, x64)
WinMenuSelectItem ahk_id %RprocID%,,2&,2& ;edit->paste

; finalize
WinActivate ahk_id %stID%
clipboard := oldclipboard

;ListVars
;pause
;return