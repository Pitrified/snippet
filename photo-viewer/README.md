## TODO

#### photo_main.py

Viene aperta l'applicazione, gestisce lui i path?
Non credo proprio, l'app deve poter aggiungere cartelle di input, e impostarsi l'output.

Qua magari fai test di performance, ma deve fare pochissimo di funzionalità effettive.

#### photo_viewer_app.py

Gestisce i layout, ti mostra solo la foto, due foto affiancate (la stessa o diverse), foto e metadata, doppia foto e metadata...

#### photo_frame.py

Mostra una singola foto. Nessun pad, nessuna informazione. Carica i metadati in un membro che viene letto dall'app se serve. Fa lo zoom (e lo fa bene, grazie).

Forse si tiene delle foto in buffer, ma se hai due frame aperti, lo devono condividere -> variabili di classe!
