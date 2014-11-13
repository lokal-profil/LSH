-- ObjMass 2.0 - samma query som 1.1, men med lite bättre kommentarer och struktur
-- Query för att filtrera ut måttuppgifter för ObjDaten, filtrerat på poster med Internet Ja och enbart LRK, SKO, SKO Bok och HWY som samling)

use mp_stockholm_lsh_50

select ObjMass.ObmId, ObjMass.ObmObjId, ObjMass.ObmTypMasseS, ObjMass.ObmMasseS, ObjAufId, AufgabeDaten.AufAufgabeS

-- ObmId är ObjMass-PK, ObmObjId är FK för ObjDaten, ObmTypMasseS är typen på mått (höjd, bredd etc.), ObmMassesS är själva måtten (inkl. enhet) och AufId är PK 
-- i AufGabeDaten där AufAufgabeS togs med som extremt förtydligande... skulle egentligen räcka med enbart AufId för att göra kopplingen till Wiki. Men jag ändrar 
-- inte SQL-strukturen mellan 1.1 och 2.0 för att underlätta för Andrés script.

from ObjMass inner join ObjDaten on ObjMass.ObmObjId = (select ObjDaten.ObjId where objdaten.ObjInternetS like '%ja%' and ObjDaten.ObjAufId = 166
or objdaten.ObjAufId = 172 or ObjDaten.ObjAufId = 175 or ObjDaten.ObjAufId = 174)
-- Urvalet görs på poster som har Internet Ja, och där det bara är Skokloster, Skoklosters boksamling, Livrustkammaren och Hallwyl som tas med (de olika AufId styr resp. samling)

inner join AufgabeDaten on AufgabeDaten.AufId = ObjDaten.ObjAufId order by ObjMass.ObmId asc
