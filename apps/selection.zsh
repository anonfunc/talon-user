# http://stackoverflow.com/questions/5407916/zsh-zle-shift-selection
# https://superuser.com/questions/604812/how-to-execute-a-function-in-bash-or-zsh-on-every-letter-being-typed-into-prompt

# Modified to match OS X selection behavior.

self-insert() {
    if ((REGION_ACTIVE)) then
       zle kill-region
    fi
    zle .self-insert
}
zle -N self-insert

r-delregion() {
    if ((REGION_ACTIVE)) then
       if [[ $MARK -lt $CURSOR ]]
       then
           zle exchange-point-and-mark
       fi
       zle kill-region
    else
       zle $1
    fi
}

# There are left/right variants of deselect and select because OS X selections are weird.
# With a selection, shift-arrows snaps the selection to the cursor, but shift-home/end will extend the selection.
# So I need to manipulate the mark and cursor to emulate those behaviors, but differently depending on which keys are pressed.
r-deselect() {
    ((REGION_ACTIVE = 0))
    zle $*
}

r-deselect-left() {
    if ((REGION_ACTIVE)) then
      if [[ $MARK -lt $CURSOR ]]
      then
        zle exchange-point-and-mark
      fi
      ((REGION_ACTIVE = 0))
      zle forward-char
    fi
    zle $*
}

r-deselect-right() {
    if ((REGION_ACTIVE)) then
      if [[ $MARK -gt $CURSOR ]]
      then
        zle exchange-point-and-mark
      fi
      ((REGION_ACTIVE = 0))
      zle backward-char
    fi
    zle $*
}

r-select() {
  ((REGION_ACTIVE)) || zle set-mark-command
  zle $*
}

r-select-left() {
  if ((REGION_ACTIVE)) then
      if [[ $MARK -lt $CURSOR ]]
      then
        zle exchange-point-and-mark
      fi
  else
    zle set-mark-command
  fi
  zle $*
}

r-select-right() {
  if ((REGION_ACTIVE)) then
      if [[ $MARK -gt $CURSOR ]]
      then
        zle exchange-point-and-mark
      fi
  else
    zle set-mark-command
  fi
  zle $*
}

r-copy() {
  if ((REGION_ACTIVE)) then
    zle copy-region-as-kill
    echo -n "${CUTBUFFER}" | pbcopy
    zle $*
  else
    echo -n '' | pbcopy
  fi
}

for key kcap seq mode widget (
    sleft   kLFT    $'\e[1;2D' select backward-char
    sright  kRIT    $'\e[1;2C' select forward-char
    sup     kri     $'\e[1;2A' select-left 'beginning-of-line exchange-point-and-mark'
    sdown   kind    $'\e[1;2B' select-right 'end-of-line exchange-point-and-mark'
    send    kEND    $'\E[1;2F' select-right end-of-line
    send2   x       $'\E[4;2~' select-right end-of-line
    shome   kHOM    $'\E[1;2H' select-left beginning-of-line
    shome2  x       $'\E[1;2~' select-left beginning-of-line
    left    kcub1   $'\EOD' deselect-left backward-char
    right   kcuf1   $'\EOC' deselect-right forward-char
    left2    x   $'\E[D' deselect-left backward-char
    right2   x   $'\E[C' deselect-right forward-char
    end     kend    $'\EOF' deselect-right end-of-line
    end2    x       $'\E4~' deselect-right end-of-line
    end3    x       $'^e' deselect-right end-of-line
    home    khome   $'\EOH' deselect-left beginning-of-line
    home2   x       $'\E1~' deselect-left beginning-of-line
    home3   x       $'^a' deselect-left beginning-of-line
    csleft  x       $'\E[1;10D' select backward-word
    csright x       $'\E[1;10C' select forward-word
    csend   x       $'\E[1;10F' select end-of-line
    cshome  x       $'\E[1;10H' select beginning-of-line
    cleft   x       $'\E[1;5D'   deselect-left backward-word
    cleft2  x       $'\Eb'   deselect-left backward-word
    cright  x       $'\E[1;5C'   deselect-right forward-word
    cright2 x       $'\Ef'   deselect-right forward-word
    del     kdch1   $'\E[3~' delregion delete-char
    bs      x       $'^?' delregion backward-delete-char
    copy    x       $'\Ew' copy copy-region-as-kill
    cut     x       $'^w' copy kill-region
    yank    x       $'^y' deselect yank
  ) {
  eval "key-$key() r-$mode $widget"
  zle -N key-$key
  bindkey ${terminfo[$kcap]-$seq} key-$key
}

zle_highlight=(region:bg=blue special:standout
              suffix:bold isearch:underline paste:bold)