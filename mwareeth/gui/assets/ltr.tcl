# LTR (Left-to-Right) configuration for Tkinter
# This script sets the text direction to LTR for the entire application

# Set the text direction to LTR
option add *justify left
option add *anchor w
option add *Menu.direction left
option add *Listbox.justify left

# Set the text direction for Text widgets
proc setTextLTR {w} {
    if {[winfo class $w] == "Text"} {
        $w configure -undo 0
        $w tag configure ltr -justify left
        $w tag add ltr 1.0 end
        $w configure -undo 1
    }
    foreach child [winfo children $w] {
        setTextLTR $child
    }
}

# Apply LTR to all existing Text widgets
setTextLTR .

# Set up a binding to apply LTR to new Text widgets
bind Text <Map> {
    %W tag configure ltr -justify left
    %W tag add ltr 1.0 end
}

# Set the text direction for Entry widgets
proc setEntryLTR {w} {
    if {[winfo class $w] == "Entry"} {
        $w configure -justify left
    }
    foreach child [winfo children $w] {
        setEntryLTR $child
    }
}

# Apply LTR to all existing Entry widgets
setEntryLTR .

# Set up a binding to apply LTR to new Entry widgets
bind Entry <Map> {
    %W configure -justify left
}