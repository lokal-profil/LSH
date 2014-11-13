-- Photo-ObjDaten samhörande nr 2.0 - har lagt till ännu en exkludering i PhmInhalt01M från 1.1 -
-- Queryn idag ignorerar tyvärr Inv.Nr. från Hallwyl eller andra konstigheter (t.ex. finns det bilder som har SKO:s kolonnr inmatade i flera inv-fältet,
-- här kommer :-tecknet med som gör att det inte går att göra om värdena med convert. Möjligen skulle det gå
-- att göra ihopkopplingar på inv.nr. i fritext, men har inte hunnit lösa detta inför 2.0 - upptäckte detta under leveransdagen.
-- jag har sorterat listan på ObjInvNrS och har manuellt raderat alla NULL-värden. I framtiden kan man göra en Derived table eller en bättre select-sats som 
-- exkluderar NULL-värdena i Select-satsen med alias - men tidsbrist gjorde att jag inte kunde fixa detta nu.
--
-- Queryn inventarienummer i fritext från photoMultiple och lägger samman dem med photo samt korrekt samling från AufgabeDaten -
-- Det finns ett mindre antal bilder som har fler än ett föremål avbildat, och inventarienummer för dessa föremål är inlagda i fritext då MuseumPlus
-- inte stödjer mer än en ObjDaten-länk från varje photo-post. 
--
-- Tanken med denna query är att undvika dubletter när man kopplar samman photoMultiple och ObjDaten (det går inte att länka direkt via inventarienummer
-- då photoMultiple inte kan särskilja på inventarienummer från olika samlingar (SKO och LRK blir dubletter), vidare finns inte ObjId i PhotoMultiple
-- vilket dock blir fallet med denna query. Det ska ju inte förekomma bildarkivsposter som har inventarienummer i fritext-fältet, men inte något
-- värde i föremålsref. (vilket är photo.PhoObjId som nedan möjliggör att särskilja antingen SKO eller LRK)

use mp_stockholm_lsh_50

select 
PhotoMultiple.PhmId,
AufgabeDaten.AufId, AufgabeDaten.AufAufgabeS, Multimedia.MulId, Photo.PhoId,

-- photomultiple.PhmTypS (filtrerar bort bort andra typer än "inventarienummer")
(select convert(int, convert(varchar(5), PhotoMultiple.PhmInhalt01M)) where PhotoMultiple.PhmTypS like 'Inventarienummer'
and PhotoMultiple.PhmInhalt01M not like '%l%' 
and PhotoMultiple.PhmInhalt01M not like '%I%'
and PhotoMultiple.PhmInhalt01M not like '%,%'
and PhotoMultiple.PhmInhalt01M not like '%enr%'  
and PhotoMultiple.PhmInhalt01M not like '%:%')
as ObjInvNrS
-- select convert är raden som omvandlar fritextvärdena (dock numeriska värden) till ett nytt int-fält där inv.nr. sparas

from photo

inner join ObjDaten on photo.PhoObjId = (select objdaten.ObjId where ObjDaten.ObjInternetS like 'Ja')
-- har ersatt left join mot inner från 1.1 för att undvika tomma värden
-- join med objdaten görs endast med inventarienr som har internet Ja (detta undviker ev. Enr och raderade filer)

inner join AufgabeDaten on ObjDaten.ObjAufId = AufgabeDaten.AufId
-- har ersatt left join mot inner från 1.1 för att undvika tomma värden

inner join photomultiple on photo.PhoId = (select photomultiple.PhmPhoId where photomultiple.PhmTypS like '%inv%')
-- kopplar photomultiple till photo via phoId (dock visas endast photoMultiple med PhmTyp "Inventarienummer")

inner join Multimedia on multimedia.MulPhoId = photo.PhoId

where Photo.PhoReferenzNrS like 'Ja' and multimedia.MulPfadS like 'R:\web\hires\%' 

 order by objinvnrs -- PhotoMultiple.PhmId asc
