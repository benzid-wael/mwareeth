# RTL (Right-to-Left) configuration for Tkinter
# This script sets the text direction to RTL for the entire application

# Set the text direction to RTL
option add *justify right
option add *anchor e
option add *Menu.direction right
option add *Listbox.justify right

# Set the text direction for Text widgets
proc setTextRTL {w} {
    if {[winfo class $w] == "Text"} {
        $w configure -undo 0
        $w tag configure rtl -justify right
        $w tag add rtl 1.0 end
        # Ensure text is right-aligned
        $w configure -undo 1
    }
    foreach child [winfo children $w] {
        setTextRTL $child
    }
}

# Apply RTL to all existing Text widgets
setTextRTL .

# Set up a binding to apply RTL to new Text widgets
bind Text <Map> {
    %W tag configure rtl -justify right
    %W tag add rtl 1.0 end
}

# Set the text direction for Entry widgets
proc setEntryRTL {w} {
    if {[winfo class $w] == "Entry"} {
        $w configure -justify right
    }
    foreach child [winfo children $w] {
        setEntryRTL $child
    }
}

# Apply RTL to all existing Entry widgets
setEntryRTL .

# Set up a binding to apply RTL to new Entry widgets
bind Entry <Map> {
    %W configure -justify right
}

# Fix for Canvas and Scrollbar alignment in RTL mode
proc fixCanvasScrollbarRTL {w} {
    if {[winfo class $w] == "Canvas"} {
        # Find parent frame
        set parent [winfo parent $w]

        # Look for scrollbars in the same parent
        foreach child [winfo children $parent] {
            if {[winfo class $child] == "Scrollbar"} {
                # Check if it's a vertical scrollbar
                if {[$child cget -orient] == "vertical"} {
                    # Move vertical scrollbar to the left side for RTL
                    pack forget $child
                    pack $child -side left -fill y
                }
            }
        }
    }

    # Process children recursively
    foreach child [winfo children $w] {
        fixCanvasScrollbarRTL $child
    }
}

# Apply Canvas/Scrollbar fix to all existing widgets
fixCanvasScrollbarRTL .

# Set up a binding to fix Canvas/Scrollbar for new widgets
bind Canvas <Map> {
    set parent [winfo parent %W]
    foreach child [winfo children $parent] {
        if {[winfo class $child] == "Scrollbar" && [$child cget -orient] == "vertical"} {
            pack forget $child
            pack $child -side left -fill y
        }
    }
}
