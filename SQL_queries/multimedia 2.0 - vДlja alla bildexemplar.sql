-- Multimedia 2.0 - Query för att visa sökvägar från multimedia-tabellen. 

use mp_stockholm_lsh_50

select 

multimedia.MulId, multimedia.MulPhoId, Multimedia.MulPfadS, Multimedia.MulDateiS, Multimedia.MulExtentS
-- multimedia är länken till bildfilerna (sökvägar). MulId = multimedia-ID, MulPfadS = sökväg, MulDateiS = filnamn, MulExtentS = filändelse
-- multimedia.MulPhoId, (= PhoId i Multimedia)

-- photo.PhoSystematikS
-- PhoSystematikS visar wiki-url - obs, att det är det generella URL-fältet i bildarkivsmodulen - egentligen är det tabellen PhotoMultiple med PhmTypS = "Wikimedia Commons" och 
-- PhmInhalt01M like '%https://comm%' som är de egentliga URL:erna - i framtiden kan fler URL:er bli aktuella, alltså andra typer av URL:er, varpå
-- det i framtida exporter kan bli aktuellt med länka in PhotoMultiple här istället.

from photo 
	inner join Multimedia on photo.PhoId = multimedia.MulPhoId 
	left join AufgabeDaten on AufgabeDaten.AufId = photo.PhoAufId
	left join ObjDaten on ObjDaten.objid = Photo.PhoObjId
	-- här kopplas multimedia, urval i bildarkivet (AufgabeDaten, se nedan), ObjDaten (samlingsmodulen) ihop med photo-tabellen
	  -- nytt i 2.0 är att man måste ha med aufgabedaten (AufId = 110 = bildarkiv) för att undvika att få med "raderade filer" i bildarkivet, utan denna fick man  med dubbla multimedia-ID för 
	  -- vissa filer. 
		
where (multimedia.MulPfadS like '%R:\web\hires\%' and multimedia.MulPfadS not like '%DOK%' and multimedia.MulPfadS not like '%HWY%' and Multimedia.MulPfadS not like '%3D%') and 

-- här börjar urvalskriterierna, tar enbart med filer med sökväg R:\web\hires, undviker DOK-serien, HWY-serien samt ett par specialfall (t.ex. 3D-bilder - notera att exkluderingen från vissa
-- delar i multimedia görs med parentes, annars fungerar inte queryn. 

Photo.PhoReferenzNrS = 'Ja' and 
-- endast bilder som har Internet = Ja - viktigt kriterium.

AufgabeDaten.AufId = 110 and
-- tar endast med urvalet "bildarkiv" (slipper därmed "raderade filer")

-- (photo.PhoSystematikS like '%https://comm%' or photo.PhoSystematikS is null) 
-- OBS, i queryn kan man här välja att ta med alla med commons-länk och tomma (raden ovan), eller enbart tomma (raden nedan) - poängen är att kunna exportera ut en kombinerad lista - både de som har 
-- Commons-länk, och de som saknar. För export 2.0 behövs nog bara lista på de som saknar värden. 

(photo.PhoSystematikS is null or photo.PhoSystematikS like '%wikipedia%')
-- OBS att det är en where-sats här inom parentes där poster som av olika anledningar har fått en wikipedia-artikel inlänkad i URL-fältet även finns med, annars missar man dessa 
-- i urvalet på att leta tomma poster i det generella URL-fältet. Möjligen kan man ändra queryn så att den istället söker på det 

and PhoObjId is not null 
-- utesluter bilder som inte har objId-länk

and (ObjDaten.ObjInventarNrS not like '%ENR%' or ObjDaten.ObjInventarNrS is null)
-- Nytt i 2.0 är även en left join till objdaten så att jag kan filtrera bort alla bilder som har en koppling till ett ENR (externa-samlingen i samlingsmodulen,

order by multimedia.MulId
-- Sorterar resultatet på MulId
 
