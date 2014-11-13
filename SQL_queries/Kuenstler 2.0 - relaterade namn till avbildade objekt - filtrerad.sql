-- Kuenstler 2.0 - lite fler kommentarer, annars inga större ändringar sedan 1.1. har preciserat vissa sökkriterier lite (t.ex. R:\web\hires\ för att undvika
-- felaktiga inlänkade bilder från t.ex. R:\master\
-- Query för namnmodulen (Kuenstler), där namn relaterade till avbildade objekt visas (till bilder med sökvägen R, och internet Ja), inkl. 
-- roll till objekt (samt vissa biografiska uppgifter)

use mp_stockholm_lsh_50

select
Obj_Kuenstler.OkuId,


ObjDaten.ObjId, ObjDaten.ObjAufId,  -- behövs ej till Wiki: ObjDaten.ObjInventarNrS, 
-- vissa fält från ObjDaten

AufgabeDaten.AufAufgabeS,
-- visar relaterad samling

Kuenstler.KueId, Kuenstler.KueVorNameS, Kuenstler.KueNameS, Obj_Kuenstler.OkuArtS, Obj_Kuenstler.OkuFunktionS, 
Obj_Kuenstler.OkuValidierungS, KuenstlerDatierung.KudArtS, KuenstlerDatierung.KudDatierungS, KuenstlerDatierung.KudJahrVonL, 
KuenstlerDatierung.KudJahrBisL, KuenstlerDatierung.KudOrtS,KuenstlerDatierung.KudLandS, kuenstler.KueFunktionS,
-- fält från Kuenstler samt från kopplingstabellen Obj_Kuenstler (där roll och verifikation anges) och kopplingstabellen KuenstlerDatierung där
-- dateringar relaterade till namnen lagras.

-- behövs ej för wiki: Multimedia.MulPfadS, multimedia.MulDateiS,multimedia.MulExtentS, 
Multimedia.MulId, 
-- fält från multimedia - sökväg till bild

photo.PhoId
-- PK från Photo (kan användas för relationer)

 from
 Kuenstler inner join Obj_Kuenstler on Kuenstler.KueId = Obj_Kuenstler.OkuKueId
 inner join ObjDaten on ObjDaten.ObjId = Obj_Kuenstler.OkuObjId
 left join KuenstlerDatierung on Kuenstler.KueId = (select KuenstlerDatierung.KudKueId where KuenstlerDatierung.KudArtS like 'levnads%')
  left join photo on photo.PhoObjId = ObjDaten.ObjId
  left join AufgabeDaten on AufgabeDaten.AufId = ObjDaten.ObjAufId
 left join Multimedia on multimedia.MulPhoId = photo.PhoId

 where kuenstler.KueStandardS like '%ja%' and ObjDaten.ObjInternetS like '%ja%' and Photo.PhoReferenzNrS like '%Ja%' and multimedia.MulPfadS like 'R:\web\hires\%' order by Multimedia.MulDateiS
 -- filtrering på enbart bilder med R:-sökväg, samt internet Ja
 
