from evaluator.din import DinResultPreProcessor
from evaluator.evaluate import PredResultEvaluator
from src.sql_parser.parser import SqlParser

# from visitor.tag_collector import TagCollector

# Test it out
# data = "SELECT foo FROM bar ORDER BY mar ASC LIMIT 10 + 1"
# data = "SELECT T1.ContId ,  T1.Continent ,  count(*) FROM CONTINENTS AS T1 JOIN COUNTRIES AS T2 ON T1.ContId  =  T2.Continent GROUP BY T1.ContId"
# data = "select foo FROM bar JOIN maz ON x JOIN foo ON y"
# data = "SELECT T1.fname ,  T1.sex FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid GROUP BY T1.stuid HAVING count(*)  >  1"
# data = "SELECT COUNT(*) FROM ( SELECT T1.CountryId ,  COUNT(*) FROM COUNTRIES AS T1 JOIN CAR_MAKERS AS T2 ON T1.CountryId  =  T2.Country GROUP BY T1.CountryId HAVING count(*)  >  2 )"
# data = "SELECT AirportName FROM Airports WHERE AirportCode NOT IN (SELECT SourceAirport FROM Flights UNION SELECT DestAirport FROM Flights)"
# data = "SELECT SourceAirport FROM Flights UNION SELECT DestAirport FROM Flights"
# data = "SELECT foo FROM bar WHERE foo = (SELECT maz FROM mar)"
# data = "SELECT foo FROM bar WHERE xar = (SELECT baz from mar EXCEPT SELECT mad FROM car) UNION SELECT maz FROM mar"
# data = "SELECT T2.name ,  T2.capacity FROM concert AS T1 JOIN stadium AS T2 ON T1.stadium_id  =  T2.stadium_id WHERE T1.year  >=  2014 GROUP BY T2.stadium_id ORDER BY count(*) DESC LIMIT 1"
# data = "SELECT T2.name FROM singer_in_concert AS T1 JOIN singer AS T2 ON T1.singer_id  =  T2.singer_id JOIN concert AS T3 ON T1.concert_id  =  T3.concert_id WHERE T3.year  =  2014"

# data = "SELECT DISTINCT T1.first_name ,  T1.last_name FROM Professionals AS T1 JOIN Treatments AS T2 WHERE cost_of_treatment  <  ( SELECT avg(costof_treatment) FROM Treatments )"
# data = "SELECT DISTINCT T1.first_name ,  T1.last_name FROM Professionals AS T1 JOIN Treatments AS T2"
# data = "SELECT * FROM bar WHERE x > 2"
# data = "SELECT name FROM (SELECT * FROM car) WHERE stadium_id NOT IN (SELECT stadium_id FROM (SELECT * FROM car))"
# data = "SELECT COUNT(*) FROM singer"
# data = "SELECT T2.name ,  count(*) FROM concert AS T1 JOIN stadium AS T2 ON T1.stadium_id  =  T2.stadium_id GROUP BY T1.stadium_id"
# data = "SELECT name, country FROM singer WHERE song_name > 10"
# data = "SELECT date FROM weather WHERE max_temperature_f  >  85"
# data = "SELECT station.name FROM station WHERE lat  <  37.5"
# data = "SELECT name FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM maz))))"
# data = "SELECT Status , Population FROM city GROUP BY Status"
# data = "SELECT name FROM airports WHERE elevation BETWEEN -50 AND 50"
# data = 'SELECT SUM ( t4.count ) FROM category AS t2 JOIN business AS t1 ON t2.business_id  =  t1.business_id JOIN category AS t3 ON t3.business_id  =  t1.business_id JOIN checkin AS t4 ON t4.business_id  =  t1.business_id WHERE t1.city  =  "Los Angeles" AND t2.category_name  =  "restaurant" AND t3.category_name  =  "Moroccan"'
# data = "SELECT s FROM t"
# data = "SELECT T1.company_name FROM Third_Party_Companies AS T1 JOIN Maintenance_Contracts AS T2 ON T1.company_id  =  T2.maintenance_contract_company_id JOIN Ref_Company_Types AS T3 ON T1.company_type_code  =  T3.company_type_code ORDER BY T2.contract_end_date DESC LIMIT 1"
# data = "SELECT T1.amenity_name FROM dorm_amenity AS T1 JOIN has_amenity AS T2 ON T1.amenid  =  T2.amenid GROUP BY T2.amenid ORDER BY count(*) DESC LIMIT 1"
# data = "SELECT T3.amenity_name FROM dorm AS T1 JOIN has_amenity AS T2 ON T1.dormid  =  T2.dormid JOIN dorm_amenity AS T3 ON T2.amenid  =  T3.amenid WHERE T1.dorm_name  =  'Smith Hall' ORDER BY T3.amenity_name"
# data = "SELECT T1.fname FROM student AS T1 JOIN lives_in AS T2 ON T1.stuid  =  T2.stuid WHERE T2.dormid IN (SELECT T2.dormid FROM dorm AS T3 JOIN has_amenity AS T4 ON T3.dormid  =  T4.dormid JOIN dorm_amenity AS T5 ON T4.amenid  =  T5.amenid GROUP BY T3.dormid ORDER BY count(*) DESC LIMIT 1)"
# data = "SELECT river_name FROM river WHERE traverse IN ( SELECT state_name FROM state WHERE population  =  ( SELECT MAX ( population ) FROM state ) )"
data = "SELECT x FROM t WHERE x > 2"

parser = SqlParser()
stmt = parser.parse(data)

pre_processor = DinResultPreProcessor('data/datasets/spider/results.csv', 'out/pred.csv')
pre_processor.process()

evaluator = PredResultEvaluator("out/pred.csv", "out/eval.csv", "data/datasets/spider/database")
evaluator.process()
# # draw_graph(stmt, 'out/test')
# # print(stmt)
# # visitor = StructureAnalyzer()
# visitor = TagCollector()
# tags = stmt.accept(visitor)
# print(tags)

# visitor = FeatureCollector()
# stmt.db_id = "concert_singer"
# stats_builder = PropsExtractor('data/datasets/spider/tables.json')

# props = stmt.accept(visitor)
# print(props)

# fs = stmt.accept(visitor)
# print(fs)

# print(stmt)
# draw_graph(stmt, "test")

# visitor = NestLevelCollector()


# prop_collector = SqlPropCollector()
# props = stmt.accept(prop_collector)

# print(props)

#
# # Give the lexer some input
# lexer.input(databack)
#
# # Tokenize
# while True:
#     tok = lexer.token()
#     if not tok:
#         break  # No more input
#     print(tok.type, tok.value, tok.lineno, tok.lexpos)
