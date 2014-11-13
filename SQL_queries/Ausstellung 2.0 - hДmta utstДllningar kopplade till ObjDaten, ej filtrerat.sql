-- Ausstellung 2.0 - queryn är inte ändrad egentligen sedan 1.1
-- Query för att hämta utställningar från Ausstellung (och museum som har haft hand om utställningen - antingen egen
-- produktion, eller extern utställning
-- Den här queryn är inte filtrerad för att sålla enbart ObjId med koppling till R: och internet ja -
-- detta för att underlätta kompletteringar av data till Wikimedia.

use mp_stockholm_lsh_50

select Ausstellung_Obj.AobId, Ausstellung.AusId, Ausstellung.AusTitelS, Ausstellung.AusOrtS, Ausstellung.AusJahrS,
Ausstellung.AusDatumVonD, Ausstellung.AusDatumBisD, Ausstellung_Obj.AobObjId, AufgabeDaten.AufAufgabeS

from Ausstellung_Obj inner join Ausstellung on Ausstellung_Obj.AobAusId = Ausstellung.AusId
inner join AufgabeDaten on AufgabeDaten.AufId = Ausstellung.AusAufId
