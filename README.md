# Anonfunc's Talon user files

[Talon](https://talonvoice.com) scripts with a "real english words" approach.

Most commands are organized around "verb adjective noun adverb".

# Installation for Talon users

Clone to `~/.talon/user`.

Most of this is focused around programming in JetBrains IDEs, so you'll want to install [this plugin](https://github.com/anonfunc/voicecode-intellij).
(Search the Marketplace for "Voicecode", it's installable that way.)

# Full bootstrapping for users new to Talon

- Install Talon from https://talonvoice.com or the #beta channel on the Talon Slack.
- (Optional but recommended) Install Dragon (discontinued, buy from Amazon/Ebay.  Physical copies included download codes.)
- (Required if using Dragon) Install Dragon [6.0.8 update](https://dnsriacontent.nuance.com/dpifm/EN/6.0.8/Dragon_14812.zip)
- (Optional, but recommended) Buy a Tobii 4C (also on Amazon)
- Start Talon, start Dragon (?).
- Follow "Installation for Talon users" instructions.

## Taxonomy of verbs:
Not comprehensive, look at the scripts for the final word.

### Go: changes the "current" location (focus, cursor, etc.) in the current application.
- `Go back`
- `Go next tab`
- `Go unread`

### Focus: changes to a different application, space or desktop.
- `Focus Slack`
- `Focus Space 5`
- `Focus 5` (Space is implied)
- `Focus next window` (Using [Amethyst](https://github.com/ianyh/Amethyst))

### Editor commands:
- Go moves the cursor: `go down`, `go line start`
- Select moves the cursor and selects:  `select all`, `select line`, `select word left`
- Clear selects and then deletes: `delete line 99`, `delete word right`

### IDE commands:
- Quick fixes: `fix this`, `fix next error`, `fix line 31`
- Dragging lines: `drag up/down`
- Going to even more things: `go next method`, `go declaration`
- Growing/shrinking selection: `select more`, `select less`
- Refactorings: `refactor signature`, `extract variable`

### Toggle:
- `Toggle Dark` (turns on screen saver)
- `Toggle history`
- `Toggle frequency`

### Repeating or Extending commands:
- `repeat 3`: For commands.
- `extend`, `extend 2`: For things like selections/deletions.  

### Misc:
- `alfred`: Launch [Alfred](https://www.alfredapp.com/)
- `snippet`: Alfred snippets
- `clippings`: Alfred clipboard manager
- `learn selection`: Saves the current selection to ~/.talon/vocab.json, which is injected into the Dragon vocab.

### Text Insertion:
- `say blah blah blah over` -> `blah blah blah`
- `acronym automated teller machine` -> `ATM`
- `tree long` -> `lon`
- `quad longer` -> `long`
- `dunder set` -> `__set__`
- `dunder quad initialize` -> `__init__` (Formatters are stackable.)
- `camel new ATM machine` -> `newAtmMachine`
- `private new ATM machine` -> `newATMMachine`
- `public new ATM machine` -> `NewATMMachine`
- `call mathod` -> `.method`
- `snake two words` -> `two_words`
- `spine two words` -> `two-words`
- `smash two words` -> `twowords`
- `sentence the quick red fox` -> `The quick red fox`
- `jargon jason` -> `json` (From `~/.talon/user/jargon.json`) 
- `title watership down` -> `Watership Down`
- `allcaps / lowcaps Proper Noun` -> `PROPER NOUN` / `proper noun`
- `string foo` / `ticks foo` -> `"foo"` `'foo'`
- `backticks foo`

## Example Nouns
- `line`
- `left/right/up/down` 
- `word left/right/up/down`
- `camel left/right/up/down` (IDE only)

## Standard Talon Alphabet
- `air bat cap drum each fine gust harp sit jury crunch look made near odd pit quench red sun trap urge vest whale plex yank zip`
- `ship air bat cap` -> `ABC`
- `ship air sunk bat cap` -> `Abc`
- `uppercase air lowercase bat cap` -> `Abc`
- `shift air bat cap` -> `Abc`

## Misc

### stubs.py

Generates .pyi files from a dump of the talon packages, so you'll have some completion in PyCharm.

### Portions from:

* [Official Example Scripts](https://github.com/talonvoice/examples)
* [zdwiel's scripts](https://github.com/dwiel/talon_community)
* [tabrat's scripts](https://github.com/tabrat/talon_user)
* [tuomassalo's scripts](https://github.com/tuomassalo/talon_user)
* [dopey's scripts](https://github.com/dopey/talon_user)
* [dwighthouse/unofficial-talonvoice-docs](https://github.com/dwighthouse/unofficial-talonvoice-docs)