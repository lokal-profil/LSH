-- ObjDaten är samlingsmodulen i MuseumPlus.
-- ObjDaten 2.0 filtrerad - Genomgången och tydligare kommentarerad inför Wikimedia Export 2.0 (2014-10-24)
-- jag har gjort lite snävare urval från R: (nu R:\web\hires\) för att undvika felaktigt inlänkade bilder.
-- I 2.0 har jag tagit bort historisk händelse som tidigare var inbakad - även ObjMultiple är borttagen. 
-- Från och med 1.1-exporten togs historiska händelser och ObjMultiple som separata queries.

--
-- Query för Samlingsmodulen (tabellnamn OjbDaten (alias objekt nedan), med relaterad data från flera andra tabeller. 
-- Central koppling är mellan ObjDaten och bildarkiv (Photo) samt multimedia (multimedia) (dock har dessa kopplingar ändrats i bort i 2.0, men exporten 
--
-- Tabellen ObjMultiple är relaterad till ObjDaten där flera olika typer av data i ObjDaten lagras, 
-- bl.a. tillverkningsort, tillverkningsland, sakord, nyckelord, etc. 
-- Tabellen AufgabeDaten är relaterad till ObjDaten gällande ID/namn på respektive samling.
--
-- Queryn saknar än så länge möjlighet att få med inventarienummer angivna i fritext i Photo-tabellen (detta löses
-- med separat query för att hålla nere antalet rader i denna query)
--
-- OBS! Denna query måste hållas filtrerad på bilder med sökvägen R:, tas filtreringen bort stiger antalet rader drastiskt... 

use mp_stockholm_lsh_50

select 
objekt.ObjId, objekt.ObjKueId, AufgabeDaten.AufId, AufgabeDaten.AufAufgabeS, 
-- PK för ObjId, samt FK för Kuenstler (namnmodulen) och AufgabeDaten (vilken samling som objekten tillhör)

objekt.ObjTitelOriginalS, objekt.ObjTitelWeitereM,
objekt.ObjInventarNrS, objekt.ObjInventarNrSortiertS, objekt.ObjReferenzNrS,
objekt.ObjDatierungS, objekt.ObjJahrVonL, objekt.ObjJahrBisL, objekt.ObjSystematikS, 
objekt.ObjFeld01M, objekt.ObjFeld02M, objekt.ObjFeld03M, objekt.ObjFeld06M, objekt.ObjReserve01M
-- här listas de fält som ska visas från ObjDaten (med aliaset objekt), bl.a. titel, beskrivning, klassifikation, etc. 

from ObjDaten as objekt 

inner join AufgabeDaten on AufgabeDaten.AufId = objekt.ObjAufId
 -- kopplar institution/samling från AufgabeDaten
 
 where objekt.ObjInternetS like 'Ja' and (AufgabeDaten.AufId = 172 or AufgabeDaten.AufId = 174 
 or AufgabeDaten.AufId = 166 or AufgabeDaten.AufId = 175 or AufgabeDaten.AufId = 179)

-- filtrerar urvalet så att endast poster med Internet Ja visas, och tar endast med objekt som tillhör
-- Livrustkammaren, Livrustkammarens boksamling, Skokloster, Skoklosters boksamling, Hallwylska museet - utan denna filtrering visades poster från "raderade filer"
-- obs, oerhört viktigt med parentesen runt alla samlingsfilter, annars säger queryn alla med internet ja och aufId 172 ELLER alla övriga 8

order by objekt.ObjId asc
