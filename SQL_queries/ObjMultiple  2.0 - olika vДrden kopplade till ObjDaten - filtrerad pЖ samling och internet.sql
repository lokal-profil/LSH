-- ObjMultiple 2.0 - enbart kommentarer som skiljer den mot 1.1. Även val av databas är tillagt för att underlätta Import/export Data-verktyget.
-- Query som filtrerar ut olika värden från ObjMultiple som är en "samlingspunkt" för många olika typer av flervalsfält i
-- ObjDaten (i ObjMultiple lagras t.ex. mått, dekor, signatur/påskrift, tillverkningsort, etc. från samlingsmodulen (ObjDaten).

use mp_stockholm_lsh_50

select ObjMultiple.OmuId, ObjMultiple.OmuObjId, ObjMultiple.OmuTypS, ObjMultiple.OmuBemerkungM, 
ObjMultiple.OmuInhalt01M, ObjDaten.ObjInventarNrS, ObjDaten.ObjAufId, AufgabeDaten.AufAufgabeS

from ObjMultiple inner join ObjDaten on ObjMultiple.OmuObjId = (select ObjDaten.ObjId where ObjDaten.ObjInternetS like 'Ja')
inner join AufgabeDaten on AufgabeDaten.AufId = (select ObjDaten.ObjAufId where objdaten.ObjAufId = 166 
or objdaten.ObjAufId = 172 or ObjDaten.ObjAufId = 175 or ObjDaten.ObjAufId = 174)
-- ObjMultiple kopplas till ObjDaten där enbart poster som har Internet Ja tas med
-- För att tydliggöra vilken samling respektive värde hör till kopplas AufgabeDaten, där endast poster tillhörande
-- Livrustkammaren, Skoklosters slott, Skoklosters slotts boksamling och Hallwylska museet visas. Detta för att undvika 
-- poster som ingår i t.ex. "Extern"-samlingen

where OmuTypS like '%signatur%' or ObjMultiple.OmuTypS like '%påskrift%' 
or ObjMultiple.OmuTypS like '%signer%' or ObjMultiple.OmuTypS like '%specifik%' or ObjMultiple.OmuTypS like '%material%'
or ObjMultiple.OmuTypS like '%teknik%' or ObjMultiple.OmuTypS like '%tillverknings%' or ObjMultiple.OmuTypS like '%sakord%'
or ObjMultiple.OmuTypS like '%titel%' or ObjMultiple.OmuTypS like '%motiv%'
or ObjMultiple.OmuTypS like '%kort%' or ObjMultiple.OmuTypS like '%nyckel%' or ObjMultiple.OmuTypS like '%kolofon%'
-- Urvalet här görs på olika typer av typer i ObjMultiple, det lagras ännu fler typer (och därmed värden) men dessa är de som behövs.

order by ObjMultiple.OmuId asc
-- här filtreras de olika typer av värden som ska visas

