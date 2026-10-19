on run argv
    set srcFile to POSIX file (item 1 of argv)
    set outFile to POSIX file (item 2 of argv)
    set AppleScript's text item delimiters to "/"
    set filename to last text item of (item 1 of argv)
    set AppleScript's text item delimiters to ""
    set docName to text 1 thru -6 of filename
    tell application "Keynote"
        set theDoc to open srcFile
        repeat 30 times
            if theDoc is not missing value then exit repeat
            delay 1
            if exists document docName then set theDoc to document docName
        end repeat
        if theDoc is missing value then error "Keynote did not open the input presentation."
        export theDoc to outFile as PDF
        close theDoc saving no
    end tell
end run
