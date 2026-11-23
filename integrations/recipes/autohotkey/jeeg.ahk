; JeeG for Windows with AutoHotkey v2 (https://www.autohotkey.com). Save as jeeg.ahk and double-click it.
;   Win+J       ask for a task (for example: gst 2500 18) and show the answer
;   Win+Shift+J run a text task on the clipboard (for example: word count, uppercase, sort lines)
; Needs JeeG installed so that `jeeg` works in a normal Command Prompt.
#Requires AutoHotkey v2.0

Clean(s) {                         ; the phrase you type goes to a command line, so refuse shell symbols
    return !RegExMatch(s, '[&|<>^"%`r`n]')
}

RunJeeG(phrase, inputText := "") {
    if !Clean(phrase) {
        MsgBox "That task has a symbol that is not allowed here.", "JeeG"
        return
    }
    tmpIn := A_Temp "\jeeg_in.txt", tmpOut := A_Temp "\jeeg_out.txt"
    try FileDelete tmpIn
    try FileDelete tmpOut
    FileAppend inputText, tmpIn, "UTF-8-RAW"
    redirect := inputText = "" ? "" : ' < "' tmpIn '"'
    RunWait A_ComSpec ' /c jeeg ' phrase redirect ' > "' tmpOut '" 2>&1', , "Hide"
    out := FileExist(tmpOut) ? FileRead(tmpOut, "UTF-8") : "No answer from JeeG. Is it installed?"
    try FileDelete tmpIn
    try FileDelete tmpOut
    return Trim(out, "`r`n ")
}

#j:: {
    ib := InputBox("What do you want to do?", "JeeG", "w420 h130")
    if ib.Result != "OK" || ib.Value = ""
        return
    out := RunJeeG(ib.Value)
    if out != ""
        MsgBox out, "JeeG"
}

#+j:: {
    ib := InputBox("Which text task for the clipboard?", "JeeG", "w420 h130", "word count")
    if ib.Result != "OK" || ib.Value = ""
        return
    out := RunJeeG(ib.Value, A_Clipboard)
    if out != "" {
        A_Clipboard := out
        MsgBox out "`n`n(Copied to the clipboard.)", "JeeG"
    }
}
