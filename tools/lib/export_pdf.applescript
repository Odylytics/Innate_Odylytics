on run argv
  set src to (item 1 of argv)
  set dst to (item 2 of argv)
  tell application "Microsoft PowerPoint"
    activate
    open (POSIX file src)
    delay 4
    set p to active presentation
    save p in (POSIX file dst) as save as PDF
    delay 3
    close p saving no
  end tell
end run
