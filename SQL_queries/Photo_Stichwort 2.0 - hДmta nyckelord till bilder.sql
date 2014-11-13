-- Photo_Stichwort 2.0 - enbart tillagd val av databas som skiljer queryn mot 1.1
-- Query som ger nyckelord till bildarkivet

use mp_stockholm_lsh_50

select Photo_Stichwort.PstId, photo.PhoId, Stichwort.StiBezeichnungS, Stichwort.StiSynonymS 

from Photo_Stichwort left join Photo on Photo_Stichwort.PstPhoId = Photo.PhoId
left join Stichwort on Photo_Stichwort.PstStiId = Stichwort.StiId order by Photo_Stichwort.PstId
