# Photo Viewer

## TODO

### general
* decent loggers

### photo\_main.py
* test performance of resize/zoom
* some cli interface might be useful
* or at least a config file, JSON?

DONE

* at least a base\_path has to be passed to pwa

### photo\_viewer\_app.py

##### Layout selection
* layouts are boring and error prone, some nested grid might help, but you need intermediate frames

DONE

* force redraw on layout change
* widgets already need to exist to be packed, the second photo\_frame has to be created immediately? At the moment, yes
* cycle through them, put code to build a layout in a function

##### Photo selection
* somewhere a dot to show whether or not the photo is in the selection

DONE

* select input folder(s) at runtime, add all the complete paths to the list of pic to cycle through
* select output folder at runtime
* `tkFileDialog.askdirectory()` to select folders
* how are changes in the input list sent to photo\_frame(s)? quite easily, send just a list and update pointer
* create (and backup existing) default output folder, no backup is needed, if the files exist they are not copied

#### UI
* all the `if layout is double` should just call `clone_frames` and do no redundant calculations

DONE

* show list of input photos and enable jumping around, (double)clickable labels
* visualizing thumbnails on a map

##### settings
* how are settings visualized? the list of input photos, selected photos, saved?
* thumbail to preview selected pictures
* are settings saved? config file?

##### metadata
* just list them
* filter with them... is it useful?
* what about sorting the list according to them? date modified, resolution
* two columns for metadata side by side
* load metadata and thumbnails asynchronously
* a Photo class might be easier to mantain to keep track of the metadata and thumbnail

##### personalized tag
* mantain a file with a list of tag for each photo... absolute paths can change too easily, how do you track that?
* tag in the metadata might be easier

### photo\_frame.py
* `set\_sort\_key` method where you set the way to sort the photo list
* change resampling - at runtime - if you are downscaling (LANCZOS) or zooming in
* move pics with mouse

DONE

* how are values shared? index, zoom\_level, mov\_xy are cloned in clone\_frames
* zoom is in a log scale, change the base to adjust the speed
* `set\_new\_list` method where the current photo name is searched in the new list and the pointer moved
* just fix the damn zoom
* `is\_hidden` filed that stops everything but pointer to be changed? change\_photo does this, synced by change\_layout
* x, y, widget are event attributes you can use to find the relative mouse pos [effbot](https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm)

## Description

#### photo\_main.py

Viene aperta l'applicazione, gestisce lui i path?
Non credo proprio, l'app deve poter aggiungere cartelle di input, e impostarsi l'output.

Qua magari fai test di performance, ma deve fare pochissimo di funzionalità effettive.

Se vuoi gli input da argparse li parsi qui dentro.

#### photo\_viewer\_app.py

Gestisce i layout, ti mostra solo la foto, due foto affiancate (la stessa o diverse), foto e metadata, doppia foto e metadata...

Mostra un help con tutti i millemila comandi da tastiera.

I comandi devono cambiare in funzione del layout, elif dentro al callback direi.

#### photo\_frame.py

Mostra una singola foto. Nessun pad, nessuna informazione. Carica i metadati in un membro che viene letto dall'app se serve. Fa lo zoom (e lo fa bene, grazie).

Forse si tiene delle foto in buffer, ma se hai due frame aperti, lo devono condividere -> variabili di classe!
