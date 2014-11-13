-- Ereignis 2.0 - ingen ändring sedan 1.1 mer än val av databas och lite kommentarer.
-- Den här queryn hämtar historiska händelser med koppling till ObjDaten

use mp_stockholm_lsh_50

select Ereignis_Obj.EroId, Ereignis.ErgId, Ereignis_Obj.EroObjId, Ereignis.ErgKurztitelS, Ereignis.ErgArtS from Ereignis_Obj 
inner join Ereignis on Ereignis_Obj.EroErgId = Ereignis.ErgId 
inner join ObjDaten on Ereignis_Obj.EroObjId = ObjDaten.ObjId 

where ObjDaten.ObjInternetS like '%ja%' order by Ereignis_Obj.EroId asc
-- väljer ut enbart de händelser som har objekt med internet ja i sig
