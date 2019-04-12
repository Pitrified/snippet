# Photo Viewer

## TODO

### photo_main.py
* test performance of resize/zoom
* some cli interface might be useful
DONE
* at least a base_path has to be passed to pwa

### photo_viewer_app.py

##### Layout selection
* force redraw on layout change
* layouts are boring and error prone, some nested grid might help, but you need intermediate frames
DONE
* widgets already need to exist to be packed, the second photo_frame has to be created immediately? At the moment, yes
* cycle through them, put code to build a layout in a function

##### Photo selection
* select input folder(s) at runtime, add all the complete paths to the list of pic to cycle through
* select output folder at runtime
* `tkFileDialog.askdirectory()` to select folders
* create (and backup existing) default output folder
* somewhere a dot to show wether or not the photo is in the selection
DONE
* how are changes in the input list sent to photo_frame(s)? quite easily, send just a list and update pointer

#### UI

##### settings
* how are settings visualized? the list of input photos, selected photos, saved?
* are settings saved? config file?

##### metadata
* just list them
* filter with them... is it useful?
* what about sorting the list according to them? date modified, resolution
* a Photo class might be easier to mantain

##### personalized tag
* mantain a file with a list of tag for each photo... absolute paths can change too easily, how do you track that?
* tag in the metadata might be easier

### photo_frame.py
* just fix the damn zoom
* x, y, widget are event attributes you can use to find the relative mouse pos [effbot](https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm)
* `is_hidden` filed that stops everything but pointer to be changed?
* how are values shared? zoom, move...
* `set_sort_key` method where you set the way to sort the photo list
* zoom is in a log scale, change the base to adjust the speed
DONE
* `set_new_list` method where the current photo name is searched in the new list and the pointer moved

## Description

#### photo_main.py

Viene aperta l'applicazione, gestisce lui i path?
Non credo proprio, l'app deve poter aggiungere cartelle di input, e impostarsi l'output.

Qua magari fai test di performance, ma deve fare pochissimo di funzionalità effettive.

Se vuoi gli input da argparse li parsi qui dentro.

#### photo_viewer_app.py

Gestisce i layout, ti mostra solo la foto, due foto affiancate (la stessa o diverse), foto e metadata, doppia foto e metadata...

Mostra un help con tutti i millemila comandi da tastiera.

I comandi devono cambiare in funzione del layout, elif dentro al callback direi.

#### photo_frame.py

Mostra una singola foto. Nessun pad, nessuna informazione. Carica i metadati in un membro che viene letto dall'app se serve. Fa lo zoom (e lo fa bene, grazie).

Forse si tiene delle foto in buffer, ma se hai due frame aperti, lo devono condividere -> variabili di classe!
