-- Get horizon of map unit
select ch.chkey, ch.cokey, 
  ch.hzdept_r as "top", ch.hzdepb_r as bottom,
  ch.dbthirdbar_r as bulk_density, ch.wthirdbar_r as field_capacity, ch.wfifteenbar_r as wilting_point,
  ch.sandtotal_r as sand, ch.claytotal_r as clay, ch.silttotal_r as silt, 
  ch.om_r as organic_matter, 
  ch.ksat_r as ksat, 
  ch.ph1to1h2o_r as ph, 
  ch.awc_r as awc
from mapunit mu
  join component co on co.mukey = mu.mukey
  join chorizon ch on ch.cokey = co.cokey
where mu.mukey = 506612
  and co.majcompflag = 'Yes'
order by "top" asc;
