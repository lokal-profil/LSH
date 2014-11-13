-- Objdaten - samhörande nummer 2.0 - ingen ändring sedan 1.1, utan enbart omsparad för att vara säker på att alla SQL:er är genomgångna.
-- den här queryn hämtar samhörande nummer, den gör dock ingen filtrering (join med t.ex. multimedia, photo och objdaten 
-- för att filtrera ut endast ObjId som är relevanta för wiki (dvs. de med bild med R:-sökväg och internet ja - 
-- det blir enklare att ta med allt när kompletteringar ska göras till André (fler bildarkivsposter/ObjId), dock filtreras sökningen så att 
-- endast poster med typen "samhör med" inkluderas.

use mp_stockholm_lsh_50

select OobId, OobObj1ID, OobObj2ID from ObjObj where OobBeziehungS like '%samhör%'
