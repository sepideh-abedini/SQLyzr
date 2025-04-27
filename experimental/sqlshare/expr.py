import re

import sqlglot

from src.parse.parser import SqlParser

parser = SqlParser()

sql = "SELECT score FROM [823].[CGbigill5x_asgff] WHERE ISNUMERIC(score)=1 AND CONVERT(NUMERIC,score) < 0.25"

sql = "SELECT [1045].[NWSblastnGBnt_no_rRNA.txt].Column2 AS GI, [1045].[NWSblastnGBnt_no_rRNA.txt].Column5 AS Description FROM [1045].[NWSblastnGBnt_no_rRNA.txt]"

sql = "SELECT * FROM [354].[1385name, question, answer, pivoted] ORDER BY 1385name ASC"

sql = "SELECT followee, COUNT(*) AS degree FROM [354].[twitter_rv.6200000] GROUP BY followee HAVING COUNT(*) >= ALL ( SELECT COUNT(*) FROM [354].[twitter_rv.6200000] GROUP BY followee )"

sql = "WITH vertices AS (SELECT followee as v FROM [354].[twitter_rv.6200000] UNION SELECT follower as v FROM [354].[twitter_rv.6200000]) SELECT v, COUNT(follower) FROM vertices LEFT OUTER JOIN [354].[twitter_rv.6200000] ON vertices.v = [354].[twitter_rv.6200000].followee GROUP BY v"


def transpile(sql):
    try:
        res = sqlglot.transpile(sql, read="tsql", write="sqlite")
    except Exception as e:
        print(e)
        res = sql
    return res


def remove_schema_refs(sql):
    pattern = re.compile(r'(?:\[[^\]]+\]|\w+)\.(\[[^\]]+\]|\w+)\.(\[[^\]]+\]|\w+)(?!\.)')
    result = re.sub(pattern, r'\1.\2', sql)
    return result


sql = "SELECT avg(T1) as Temperature FROM ( SELECT distinct cast(floor(ts) + floor((ts - floor(ts))*24*60 / binsize)*binsize / (24*60) as datetime) as binid , * FROM ( SELECT *, cast(time as float) as ts, 3.0 as binsize FROM [1002].[Tokyo_0_merged_data.csv] ) x ) bins GROUP BY binid"

sql = "SELECT binid , avg(T1) as Temperature , avg(S) as Salinity FROM ( SELECT distinct cast(floor(ts) + floor((ts - floor(ts))*24*60 / binsize)*binsize / (24*60) as datetime) as binid , * FROM ( SELECT *, cast(time as float) as ts, 3.0 as binsize FROM [1002].[Tokyo_0_merged_data.csv] ) x ) bins GROUP BY binid "

sql = "SELECT T1 , C1 , S , SV , T2 , case when [X.NO3..uMol.L.] = 'NA' then NULL else [X.NO3..uMol.L.] end as Nitrate , case when [O2.Conc..uM.] = 'NA' then NULL else [O2.Conc..uM.] end as Oxygen , case when o.time = '12.03' then NULL else o.time end as time , case when o.date = '5.46' then NULL else o.date end as date , case when o.[long.dc] = 'NA' then NULL else o.[long.dc] end as longitude , case when o.[lat.dc] = 'NA' then NULL else o.[lat.dc] end as latitude FROM [1002].[Tokyo_0_optode.csv] o, [1002].[Tokyo_0_tsg.csv] t, [1002].[Tokyo_0_suna.csv] s WHERE o.date = t.date AND o.date = s.date AND t.date = s.date AND o.time = t.time AND o.time = s.time AND t.time = s.time order by o.date"

sql = "select MothersAgeRecode9, MothersMaritalStatus, count( * ) from [1144].[table_natality-20k.csv] group by MothersAgeRecode9, MothersMaritalStatus with cube"

sql = "SELECT count([Plasmid]) FROM [71].[PlasmidDNA1.csv] group by UPPER(LEFT([Plasmid],1))"

sql = "SELECT species, subspec, name, bodymass FROM [71].[Birds.csv] WHERE id >= 1 and id <= 20"

# sql = "SELECT 'historic' as datasource , OBSERVER_ID , species_id as Species_code , NULL as common_name , NULL as scientific_name , question as questionable , state , county , NULL as date , year , month , NULL as day , convert(varchar(max), lat) as LATITUDE , convert(varchar(max), long) as LONGITUDE , source , quantity , estimate , habitat1 as habitat1 , null as habitat2 , comments , null as family FROM [1231].[NatureMapping_historic1.csv] UNION SELECT 'arboretum' as datasource , Obs_id , NULL as species_code , species as common_name , NULL as scientific_name , q as questionable , st as state , cast(Co as varchar(max)) as county , convert(datetime, [date]) as date , datepart(year, convert(datetime, [date])) as year , datepart(month, convert(datetime, [date])) as month , datepart(day, convert(datetime, [date])) as day , convert(varchar(max), latitude) as latitude , convert(varchar(max), longitude) as longitude , cast(source as varchar(max)) as source , qty as quantity , null as estimate , habitat as habitat1 , null as habitat2 , comment as comments , species_type as family FROM [1231].[ArboretumData.csv] UNION SELECT 'online_export' as datasource , OBSERVER_ID , Species_id as species_code , SPECIES_NAME as common_name , null as scientific_name , case when QUESTION = 'Sure' THEN 1 ELSE 0 END as questionable , STATE , COUNTY , convert(datetime, OBSERVATION_DATE) as date , datepart(year, convert(datetime, OBSERVATION_DATE)) as year , datepart(month, convert(datetime, OBSERVATION_DATE)) as month , datepart(day, convert(datetime, OBSERVATION_DATE)) as day , convert(varchar(max), latitude) as latitude , convert(varchar(max), longitude) as longitude , SOURCE , QUANTITY , ESTIMATE , HABITAT1 , habitat2 , COMMENTS , null as family FROM [1231].[online_export_080410_edit.csv] UNION SELECT 'ebird' as datasource , NULL as OBSERVER_ID , convert(varchar(max), species_code) as species_code , common_NAME as common_name , null as scientific_name , case when QUESTION = 'Not valid and reviewed' OR QUESTION = 'Not valid but not reviewed' THEN 0 ELSE 1 END as questionable , STATE , COUNTY , date as date , years as year , months as month , days as day , convert(varchar(max), latitude) as latitude , convert(varchar(max), longitude) as longitude , NULL as SOURCE , QUANTITY , null as ESTIMATE , null as HABITAT1 , null as habitat2 , COMMENTS , null as family FROM [1231].[xls_ebird_WA_history.txt]"

sql = "SELECT CONVERT(datetime, time, 3) FROM [1057].[Tokyo_1_sds_1.csv]"

sql = "SELECT cruise , [file] , cast([time] as datetime2) as time , lat , lon , opp_evt_ratio , flow_rate , file_duration , pop , n_count , abundance , fsc_small , chl_small , pe FROM [1059].[stat.csv]"

sql = "SELECT p.DEST FROM [372].[flights09_part] AS c JOIN (SELECT  * FROM [372].[flights09_part] LIMIT 1) AS p ON p.TAIL_NUM = c.TAIL_NUM AND (p.DATE < c.date OR (p.DATE = c.DATE AND p.ARR_TIME <= c.DEP_TIME)) WHERE p.DEST != c.ORIGIN"

sql = "SELECT score FROM [823].[CGbigill5x_asgff] WHERE ISNUMERIC(score)=1 AND CONVERT(NUMERIC,score) < 0.25 "

sql = "SELECT DATETIMEFROMPARTS(2000+year,month,day,hour, minute,second,0) as timestamp FROM [1057].[Tokyo1_uway_timestamp]"

# sql = "SELECT [table_1385s_1.csv].1385name FROM [718].[table_1385s_1.csv] WHERE major = 'history'"
sql = "SELECT s.2x from b"

sql = "SELECT CAST(CAST([GMT date] AS DATE) AS DATETIME) + CAST([GMT time] AS TIME) FROM [1057].[Thompson0_uway.csv]"

sql = "select cast(x as INTEGER) from y"

sql = "SELECT min(timestamp) FROM [1002].[Tokyo_0_merged.csv]"

sql = "SELECT * FROM [1117].[table_OrcaMaster2010.csv] SELECT * FROM [1117].[table_OrcaMaster2010.csv] WHERE Pod = 'J' "

sql = "SELECT Seqname , CASE WHEN CHARINDEX(';', GroupID) = 0 THEN GroupID ELSE SUBSTRING(GroupID, 1, CHARINDEX(';', GroupID)- 1) END AS GroupID , CASE WHEN CHARINDEX(';', GroupID) = 0 THEN '' ELSE SUBSTRING(GroupID, CHARINDEX(';', GroupID)+1, LEN(GroupID)) END AS Comment FROM [354].[txt.gff]"
sql = "SELECT -2 from b"

sql = "SELECT binid from ( SELECT source  S , SV , T2 FROM ( select month + '/' + day + '/' + year as ddate  , * from ( select substring(sdate,1,2) as day , substring(sdate,3,2) as month , substring(sdate,5,2) as year , substring(ztime,len(ztime) - 5,6) as stime , * from ( select '00000' + cast(time as varchar) as ztime , cast(date as varchar) as sdate , * from [1002].[Tokyo_tsg_cleaned] ) x ) y ) z ) 1358 where isdate(binid) = 0"

sql = "SELECT cast(S.LAT as INT)/100 as LATdeg, S.LAT - (cast(S.LAT as INT)/100) as LATmin, cast(S.LON as INT)/100 as LONdeg, S.[file],T.[OCEAN.TEMP],T.SALINITY,S.day FROM [1057].[KiloMoana_1_sds_timestamp_1col_snapshot] as S, [1057].[KiloMoana1_sds_TS_snapshot] as T WHERE S.timestamp = T.timestamp"

sql = "SELECT res_type_sh, pdb_id, res_index AS K FROM [1267].[h2_w_2.csv] WHERE res_type_sh ='K'; SELECT res_type_sh, pdb_id, res_index AS R FROM [1267].[h2_w_2.csv] WHERE res_type_sh ='R';"

sql = "SELECT cruise , CASE WHEN NOT cruise LIKE '%[^0-9]%' THEN 1 ELSE 0 END as cruisenum , [file] , cast([time] as datetime2) as time , lat , isnumeric(lat) as latnum , lon , opp_evt_ratio , flow_rate , file_duration , pop , n_count , CAST(CASE WHEN isnumeric(abundance) = 0 THEN NULL ELSE abundance END as FLOAT) as abundance , fsc_small , chl_small , pe FROM [277].[stat.csv] ORDER BY [time] DESC"

sql = "SELECT res_type_sh, pdb_id, res_index AS k FROM [1267].[h2_w_2.csv] WHERE res_type_sh ='K'; SELECT res_type_sh, pdb_id, res_index AS r FROM [1267].[h2_w_2.csv] WHERE res_type_sh ='R'; SELECT * FROM k, r WHERE k.res_index = r.res_index-1;"

sql = 'Select * From [1123].[BSoysterGENE] Left join [1123].[Mgo Expression (RPKM)] ON [BSoysterGENE].ID=[1123].[Mgo Expression (RPKM)]."." '

# sql = "SELECT * ,(Column3 * 2.000),(round(length,.1)) FROM [1123].[Oyster Genes with CG ratio per loci]"

sql = "SELECT .0 FROM queries "

sql = "(select p.k as id, f1.v as title, f2.v as year, f3.v as venue, p.p as type from pub p, field f1, field f2, field f3 where p.k = f1.k and p.k = f2.k and p.k = f3.k and f1.p = 'title' and f2.p = 'year' and f3.p = 'booktitle' and p.p='inproceedings') UNION (select p.k as id, f1.v as title, f2.v as year, f3.v as venue, p.p as type from pub p, field f1, field f2, field f3 where p.k = f1.k and p.k = f2.k and p.k = f3.k and f1.p = 'title' and f2.p = 'year' and f3.p = 'journal' and p.p='article') UNION (select p.k as id, f1.v as title, f2.v as year, null as venue, p.p as type from pub p, field f1, field f2 where p.k = f1.k and p.k = f2.k and f1.p = 'title' and f2.p = 'year' and p.p='book') UNION (select p.k as id, f1.v as title, f2.v as year, null as venue, p.p as type from pub p, field f1, field f2 where p.k = f1.k and p.k = f2.k and f1.p = 'title' and f2.p = 'year' and p.p like '%thesis')"
sql = "select distinct journal from article where journal in ('PVLDB', 'VLDB J.','ACM Trans. Database Syst.','IEEE Database Eng. Bull.') select a.fullname, count( * ) as totalPUBS from [1143].author a, [1143].authored b, [1143].publication q, [1143].article p where a.fullname = b.fullname and b.pubID = q.id and q.year >= 1995 and q.year <= 2005 and q.id = p.id and p.journal in ('PVLDB', 'VLDB J.','ACM Trans. Database Syst.','IEEE Database Eng. Bull.') group by a.fullname order by count( * ) desc"
sql = "SELECT * ,((Column3^10000)/(length^10000)) FROM [1123].[Oyster Genes with CG ratio per loci]"
sql = "SELECT CAST([Time] AS Datetime) AS [DateTime] , DATEDIFF(SECOND,{d '1970-01-01'}, CAST([Time] AS Datetime)) AS [UnixTimestamp] , [LAT] , [LON] , CASE WHEN [CONDUCTIVITY] = 'NA' THEN NULL ELSE [CONDUCTIVITY] END AS [CONDUCTIVITY] , [SALINITY] , [OCEAN.TEMP] , [BULK.RED] , [STREAM.PRESSURE] , [FILTER.PRESSURE] , CASE WHEN [MACHINE.TEMP] = 'NA' THEN NULL ELSE [MACHINE.TEMP] END AS [MACHINE.TEMP] , [Xaccel] , [Yaccel] , [Zaccel] , [MILLISECOND.TIMER] , [LASER.POWER] , [EVENT.RATE] , [FLOW.METER] , CASE WHEN [position] = 'NA' THEN NULL ELSE [position] END AS [position] , [CHL] , [LightTrans] , [acqError] , [D1D2] , CASE WHEN [PAR] = 'NA' THEN NULL ELSE [PAR] END AS [PAR] , [time] , [day] , [file] , [DMY] , [HMS] FROM [1059].[sds2.tab] ORDER BY [DateTime] ASC"
sql = "select count( * ) from [proteins_cleaved_pdb] where top_pdb <> '' / * select cleaved, count( * ) from [xstal_tracker.csv] x left join [proteins_cleaved_pdb] p on (x.[protein code-1] = p.ssgcidid) where x.[Initial trials set up] < '05-01-2011' and top_pdb <> '' group by cleaved * /"

sql = "SELECT M1ID,M1ratio,T1D3ratio,T1D5ratio,((m1ratio + T1D3ratio + T1D5ratio)/3) as mean_1lin, (Select max(v) from (values (M1ratio), (T1D3ratio), (T1D5ratio)) as value(v)) as [Max] FROM [1123].[filt3_M1]m1 join [1123].[filt3_M3]m3 on m1.M1ID=m3.M3ID join [1123].[filt3_T1D3]t1d3 on m1.M1ID=t1d3.T1D3ID join [1123].[filt3_T1D5]t1d5 on m1.M1ID=t1d5.T1D5ID join [1123].[filt3_T3D3]t3d3 on m1.M1ID=t3d3.T3D3ID join [1123].[filt3_T3D5]t3d5 on m1.M1ID=t3d5.T3D5ID where [M1coverage] >= '5' and [M3coverage] >= '5' and [T1D3coverage] >= '5' and [T1D5coverage] >= '5' and [T3D3coverage] >= '5' and [T3D5coverage] >= '5'"

sql = "SELECT * , sperm.mean_sperm-d3.mean_day3 as 1358 FROM [1123].[br_cglarv_sperm.txt]sperm inner join [1123].[br_cglarv_day3.txt]d3 on sperm.loci=d3.loci inner join [1123].[br_cglarv_day5.txt]d5 on sperm.loci=d5.loci where abs(sperm.mean_sperm-d3.mean_day3) > 0.3 or abs(sperm.mean_sperm-d5.mean_day5) > 0.3 or abs(d3.mean_day3-d5.mean_day5) > 0.3"
sql = "select count( * ) from 1385_queries where 1=1 select * from 1385_queries where short_desc like '%orca%'"
sql = "SELECT species, subspec, name, bodymass FROM [71].[Birds.csv] WHERE id > = 1 and id <= 20"
sql = "select distinct sv.construct, (select sv2.dnasamplename + ',' from [s89_SV_v2.csv] sv2 where sv2.construct = sv.construct for xml path('')) as seq_runs, (select sv3.status + ',' from [s89_SV_v2.csv] sv3 where sv3.construct = sv.construct for xml path('')) as status from [s89_SV_v2.csv] sv "
sql = "select x.[Initial trials set up] from [proteins_cleaved_pdb] p join [xstal_tracker.csv] x on (x.[protein code-1] = p.ssgcidid and x.[Initial trials set up] <> '') where top_pdb <> '' order by x.[Initial trials set up] desc select cleaved, count( * ) from [xstal_tracker.csv] x left join [proteins_cleaved_pdb] p on (x.[protein code-1] = p.ssgcidid) where x.[Initial trials set up] < '05-01-2011' and top_pdb <> '' group by cleaved"
sql = 'SELECT * FROM [1123].[table_QPX_Experiment_UniqueReads_simple.txt] Left JOIN [1123].[QPX_CLC_experiment_Kal_tab.txt] ON [1123].[table_QPX_Experiment_UniqueReads_simple.txt]."Feature ID"=[1123].[QPX_CLC_experiment_Kal_tab.txt]."Feature ID"'
# sql = 'SELECT ROW_NUMBER() OVER (PARTITION BY TAIL_NUM, ORIGIN, DEST, EARLIEST, ETIME ORDER BY TAIL_NUM), f. * , o.Latitude oLat, o.Longitude oLon, d.Latitude dLat, d.Longitude dLon FROM [372].[ghost_flights] f JOIN [372].[airports] o ON f.ORIGIN = o."IATA/FAA" JOIN [372].[airports] d ON f.DEST = d."IATA/FAA"'
# sql = "SELECT ROW_NUMBER() OVER (PARTITION BY TAIL_NUM ORDER BY YEAR, MONTH, DAY_OF_MONTH, DEP_TIME) ID, ORIGIN, DEST, TAIL_NUM, FL_NUM, DATEFROMPARTS(YEAR, MONTH, DAY_OF_MONTH) DATE, CARRIER, DEP_TIME, ARR_TIME, DISTANCE, AIR_TIME FROM [372].[flights09] a WHERE TAIL_NUM != '' AND '' != ALL( SELECT ARR_TIME FROM [372].[flights09] b WHERE a.TAIL_NUM = b.TAIL_NUM) AND '' != ALL( SELECT DEP_TIME FROM [372].[flights09] b WHERE a.TAIL_NUM = b.TAIL_NUM)"
sql = "SELECT * FROM [1117].[table_OrcaMaster2010.csv] SELECT * FROM [1117].[table_OrcaMaster2010.csv] WHERE Pod = 'J'"
sql = "select distinct journal from article where journal in ('PVLDB', 'VLDB J.','ACM Trans. Database Syst.','IEEE Database Eng. Bull.')select a.fullname, count( * ) as totalPUBS from [1143].author a, [1143].authored b, [1143].publication q, [1143].article p where a.fullname = b.fullname and b.pubID = q.id and q.year >= 1995 and q.year <= 2005 and q.id = p.id and p.journal in ('PVLDB', 'VLDB J.','ACM Trans. Database Syst.','IEEE Database Eng. Bull.') group by a.fullname order by count( * ) desc;"
sql = "SELECT * , A1+A2+A3+B1+B2+ B3+C1+C2+C3+D1+D2+ +D3+E1+E2+F1+ F2+F3+G1+G2+G3+ H1+H2+H3+J1+J2+J3+ L1+L2+L3+M1+M2+M3+M1+[N1]+N2+ N3 AS [protein presence] FROM [412].[rpom peptide and protein presence]"

sql = 'Select * From [1123].[TJGR_Gene_SPID_evalue_Description] Inner join [1123].[AggCo Oyster Bisulfite mRNA and CDS] ON [TJGR_Gene_SPID_evalue_Description].Column1=[AggCo Oyster Bisulfite mRNA and CDS].ID SELECT * FROM [1123].[AggCo Oyster Bisulfite mRNA and CDS] Where "SUM mRNA" > 100 and "Ratio mCDS/mIntron" > 3'
sql = "SELECT * , ('EMP'+right('00'+CONVERT([varchar](5),[start]),(5))) FROM [1123].[Zhang_Mgo_gene_RNA-seq_IGV]"

sql = "SELECT M1ID,M1ratio,T1D3ratio,T1D5ratio,((m1ratio + T1D3ratio + T1D5ratio)/3) as mean_1lin, (Select max(v) from (values (M1ratio), (T1D3ratio), (T1D5ratio)) as value(v)) as [Max] FROM [1123].[filt3_M1]m1 join [1123].[filt3_M3]m3 on m1.M1ID=m3.M3ID join [1123].[filt3_T1D3]t1d3 on m1.M1ID=t1d3.T1D3ID join [1123].[filt3_T1D5]t1d5 on m1.M1ID=t1d5.T1D5ID join [1123].[filt3_T3D3]t3d3 on m1.M1ID=t3d3.T3D3ID join [1123].[filt3_T3D5]t3d5 on m1.M1ID=t3d5.T3D5ID where [M1coverage] >= '5' and [M3coverage] >= '5' and [T1D3coverage] >= '5' and [T1D5coverage] >= '5' and [T3D3coverage] >= '5' and [T3D5coverage] >= '5'"

sql = "SELECT 'arboretum' as datasource , Obs_id , NULL as species_code , species as common_name , NULL as scientific_name , q as questionable , st as state , cast(Co as varchar(max)) as county FROM [1231].[ArboretumData.csv] UNION SELECT 'online_export' as datasource , OBSERVER_ID , Species_id as species_code , SPECIES_NAME as common_name , null as scientific_name , case when QUESTION = 'Sure' THEN 1 ELSE 0 END as questionable , STATE , COUNTY FROM [1231].[online_export_080410_edit.csv]"

sql = "select * from 1385_queries  name like '%table_%'"

sql = "select count( * ) from 1385_queries where not (sql_code like '%table_%' and sql_code not like '%AND%' and sql_code not like '%JOIN%')"
sql = "select count( * ) from 1385_queries where 1=1 and not (sql_code like '%table_%' and sql_code not like '%AND%' and sql_code not like '%JOIN%') and is_public = 1 "

sql = "select count( * ) from 1385_queries where 1=1 select * from 1385_queries where short_desc like '%orca%'"

sql = "SELECT followee, COUNT(*) AS degree FROM [354].[twitter_rv.6200000] GROUP BY followee HAVING COUNT(*) >= ( SELECT COUNT(*) FROM [354].[twitter_rv.6200000] GROUP BY followee ) "

sql = "SELECT * , A1+A2+A3+B1+B2+ B3+C1+C2+C3+D1+D2+ D3+E1+E2+F1+ F2+F3+G1+G2+G3+ H1+H2+H3+J1+J2+J3+ L1+L2+L3+M1+M2+M3+M1+[N1]+N2+ N3 AS [protein presence] FROM [412].[rpom peptide and protein presence]"

sql = "SELECT * ,((Column3^10000)/(length^10000)) FROM [1123].[Oyster Genes with CG ratio per loci]"

sql = "SELECT * , ('EMP'+right('00'+CONVERT([varchar](5),[start]),(5))) FROM [1123].[Zhang_Mgo_gene_RNA-seq_IGV] "

sql = "SELECT M1ID,M1ratio,T1D3ratio,T1D5ratio,((m1ratio + T1D3ratio + T1D5ratio)/3) as mean_1lin, (Select max(v) from (values (M1ratio), (T1D3ratio), (T1D5ratio)) as value(v)) as [Max] FROM [1123].[filt3_M1]m1 join [1123].[filt3_M3]m3 on m1.M1ID=m3.M3ID join [1123].[filt3_T1D3]t1d3 on m1.M1ID=t1d3.T1D3ID join [1123].[filt3_T1D5]t1d5 on m1.M1ID=t1d5.T1D5ID join [1123].[filt3_T3D3]t3d3 on m1.M1ID=t3d3.T3D3ID join [1123].[filt3_T3D5]t3d5 on m1.M1ID=t3d5.T3D5ID where [M1coverage] >= '5' and [M3coverage] >= '5' and [T1D3coverage] >= '5' and [T1D5coverage] >= '5' and [T3D3coverage] >= '5' and [T3D5coverage] >= '5'"

sql = "SELECT * , sperm.mean_sperm-d3.mean_day3 as 1358 FROM [1123].[br_cglarv_sperm.txt]sperm inner join [1123].[br_cglarv_day3.txt]d3 on sperm.loci=d3.loci inner join [1123].[br_cglarv_day5.txt]d5 on sperm.loci=d5.loci where abs(sperm.mean_sperm-d3.mean_day3) > 0.3 or abs(sperm.mean_sperm-d5.mean_day5) > 0.3 or abs(d3.mean_day3-d5.mean_day5) > 0.3 "

sql = "SELECT 'arboretum' as datasource , Obs_id , NULL as species_code , species as common_name , NULL as scientific_name , q as questionable , st as state , cast(Co as varchar(max)) as county FROM [1231].[ArboretumData.csv] UNION SELECT 'online_export' as datasource , OBSERVER_ID , Species_id as species_code , SPECIES_NAME as common_name , null as scientific_name , case when QUESTION = 'Sure' THEN 1 ELSE 0 END as questionable , STATE , COUNTY FROM [1231].[online_export_080410_edit.csv]"

sql = "SELECT 'historic' as datasource , OBSERVER_ID , species_id as Species_code , NULL as common_name , NULL as scientific_name , question as questionable , state , county , NULL as date FROM [1231].[NatureMapping_historic1.csv] UNION SELECT 'arboretum' as datasource , Obs_id , NULL as species_code , species as common_name , NULL as scientific_name , q as questionable , st as state , cast(Co as varchar(max)) as county , convert(datetime, [date]) as date FROM [1231].[ArboretumData.csv] "

sql = "SELECT f1.doc_id, f2.doc_id, sum(f1.frequency * f2.frequency) / ( sqrt(sum(f1.frequency^2)) * sqrt(sum(f2.frequency^2)) ) as similarity FROM [reuters_terms.csv] f1 , [reuters_terms.csv] f2 WHERE f1.doc_id = f2.doc_id AND f1.term_id = f2.term_id GROUP BY f1.doc_id, f2.doc_id"

sql = "SELECT f1.doc_id, f2.doc_id, sum(f1.frequency * f2.frequency) / ( sqrt(sum(f1.frequency^2)) * sqrt(sum(f2.frequency^2)) ) as similarity FROM [reuters_terms.csv] f1 , [reuters_terms.csv] f2 WHERE f1.doc_id = f2.doc_id AND f1.term_id = f2.term_id GROUP BY f1.doc_id, f2.doc_id"

sql = "SELECT CAST([Time] AS Datetime) AS [DateTime] , DATEDIFF(SECOND,{d '1970-01-01'}, CAST([Time] AS Datetime)) AS [UnixTimestamp] , [pop] , [resamp] , [lat] , [long] , [flow] , [bulk_red] , [salinity] , [temperature] , [event_rate] , [fluorescence] , [evt] , [opp] , [n] , [conc] , [fsc_small_mean] , [fsc_small_median] , [fsc_small_sd] , [fsc_small_mode] , [fsc_small_width] , [fsc_small_npeaks] , [fsc_perp_mean] , [fsc_perp_median] , [fsc_perp_sd] , [fsc_perp_mode] , [fsc_perp_width] , [fsc_perp_npeaks] , [fsc_big_mean] , [fsc_big_median] , [fsc_big_sd] , [fsc_big_mode] , [fsc_big_width] , [fsc_big_npeaks] , [pe_mean] , [pe_median] , [pe_sd] , [pe_mode] , [pe_width] , [pe_npeaks] , [chl_small_mean] , [chl_small_median] , [chl_small_sd] , [chl_small_mode] , [chl_small_width] , [chl_small_npeaks] , [chl_big_mean] , [chl_big_median] , [chl_big_sd] , [chl_big_mode] , [chl_big_width] , [chl_big_npeaks] , [day] , [file] , [time] FROM [1059].[stats.tab] ORDER BY [DateTime] ASC "

sql = "select count( * ) from [proteins_cleaved_pdb] where top_pdb <> '' select cleaved, count( * ) from [xstal_tracker.csv] x left join [proteins_cleaved_pdb] p on (x.[protein code-1] = p.ssgcidid) where x.[Initial trials set up] < '05-01-2011' and top_pdb <> '' group by cleaved "

sql = "SELECT CAST([Time] AS Datetime) AS [DateTime] , DATEDIFF(SECOND,{d '1970-01-01'}, CAST([Time] AS Datetime)) AS [UnixTimestamp] , [LAT] , [LON] , CASE WHEN [CONDUCTIVITY] = 'NA' THEN NULL ELSE [CONDUCTIVITY] END AS [CONDUCTIVITY] , [SALINITY] , [OCEAN.TEMP] , [BULK.RED] , [STREAM.PRESSURE] , [FILTER.PRESSURE] , CASE WHEN [MACHINE.TEMP] = 'NA' THEN NULL ELSE [MACHINE.TEMP] END AS [MACHINE.TEMP] , [Xaccel] , [Yaccel] , [Zaccel] , [MILLISECOND.TIMER] , [LASER.POWER] , [EVENT.RATE] , [FLOW.METER] , CASE WHEN [position] = 'NA' THEN NULL ELSE [position] END AS [position] , [CHL] , [LightTrans] , [acqError] , [D1D2] , CASE WHEN [PAR] = 'NA' THEN NULL ELSE [PAR] END AS [PAR] , [time] , [day] , [file] , [DMY] , [HMS] FROM [1059].[sds2.tab] ORDER BY [DateTime] ASC "
sql = "select r.term_id, r.doc_id, r.frequency/m.maxf * log((select count(distinct doc_id) from reuters) / i.occurrences) as tfidf from reuters r join ( select term_id, count( * ) as occurrences from reuters group by term_id ) i on i.term_id = r.term_id join ( select doc_id, max(frequency) as maxf from reuters group by doc_id ) m on m.doc_id = r.doc_id order by tfidf desc "
sql = " select * from 1314howe"
sql = "SELECT 'arboretum' as datasource , Obs_id , NULL as species_code , species as common_name , NULL as scientific_name , q as questionable , st as state , cast(Co as varchar(max)) as county FROM [1231].[ArboretumData.csv] UNION SELECT 'online_export' as datasource , OBSERVER_ID , Species_id as species_code , SPECIES_NAME as common_name , null as scientific_name , case when QUESTION = 'Sure' THEN 1 ELSE 0 END as questionable , STATE , COUNTY FROM [1231].[online_export_080410_edit.csv] "
sql = "select term_id, doc_id, frequency, (cast(frequency as float) / (select  cast(frequency as float) as docFreq from [1314howe].[reuters_terms.csv] A where A.doc_id = Z.doc_id order by frequency desc LIMIT 1) * IDF "

sql = "SELECT text FROM tweets WHERE text LIKE '%intern%'"

# sql = "SELECT [table_1385s_1.csv].1385name, [table_1385s_1.csv].major FROM [718].[table_1385s_1.csv] WHERE major = 'history'"

# sql = transpile(sql)[0]
print(sql)
ast = parser.parse(sql)
print(ast)
