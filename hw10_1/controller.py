import pymysql
from dbutils.pooled_db import PooledDB
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from config import DB_HOST, DB_USER, DB_PASSWD, DB_NAME

pool = PooledDB(creator=pymysql,
			host=DB_HOST,
			user=DB_USER,
			password=DB_PASSWD,
			database=DB_NAME,
			maxconnections=1,
			blocking=True)
app = FastAPI()


class BasinShort(BaseModel):
	basinId: int
	name: str

@app.get("/basins")
def get_basins() -> list[BasinShort]:
	with pool.connection() as conn, conn.cursor() as cs:
		cs.execute("""
		SELECT basin_id, ename FROM basin
		""")
	result = [BasinShort(basinId=basin_id, name=ename) for basin_id, ename in cs.fetchall()]
	return result

class BasinFull(BaseModel):
	basin_id: int
	name: str
	area: float
@app.get("/basins/{basinId}")
def get_basin_details(basinId: int) -> BasinFull:
	with pool.connection() as conn, conn.cursor() as cs:
		cs.execute("""
		SELECT basin_id, ename, area
		FROM basin
		WHERE basin_id=%s
		""", [basinId])
	result = cs.fetchone()
	if result:
		basin_id, ename, area = result
		return BasinFull(basin_id=basin_id, name=ename, area=area)
	else:
		raise HTTPException(status_code=404, detail="Basin not found")
	
# /basins/{basinId}/stations
class StationShort(BaseModel):
	station_id: int
	basin_id: int
	name: str

@app.get("/basins/{basinId}/stations")
def get_statsion_by_basin_id(basinId: int) -> list[StationShort]:
	with pool.connection() as conn, conn.cursor() as cs:
		cs.execute("""
		SELECT st.station_id, st.basin_id, st.ename
		FROM basin bs

		INNER JOIN station st
		ON bs.basin_id = st.basin_id
		WHERE bs.basin_id = %s
		""", [basinId])
	result = [StationShort(station_id=station_id, basin_id=basin_id,  name=ename) for station_id, basin_id, ename in cs.fetchall()]
	return result

class StationFull(BaseModel):
	station_id: int
	basin_id: int
	ename: str
	tname: str
	lat: float
	lon: float
@app.get("/stations/{stationId}")
def get_station_detail(stationId: int) -> StationFull:
	with pool.connection() as conn, conn.cursor() as cs:
		cs.execute("""
		SELECT station_id, basin_id, ename, tname, lat, lon
		FROM station
		WHERE station_id = %s
		""", [stationId])
	result = cs.fetchone()
	if result:
		station_id, basin_id, ename, tname, lat, lon = result
		return StationFull(
			station_id=station_id,
			basin_id=basin_id,
			ename=ename,
			tname=tname,
			lat=lat,
			lon=lon
		)
	else:
		raise HTTPException(status_code=404, detail="Basin not found")
	

class StationYearAmount(BaseModel):
	basin_id: int
	year: int
	rainfall: float

@app.get("/basins/{basinId}/annualRainfalls/{year}")
def get_rainfall_by_year_and_basinId(basinId: int, year: int):
	with pool.connection() as conn, conn.cursor() as cs:
		cs.execute("""
		SELECT bs.basin_id, rf.year, SUM(rf.amount) as rainfall
		FROM basin bs

		INNER JOIN station st
		ON bs.basin_id = st.basin_id

		INNER JOIN rainfall rf
		ON st.station_id = rf.station_id
		WHERE bs.basin_id = %s
		AND rf.year = %s

		GROUP BY bs.basin_id, rf.year
		""", [basinId, year])
	result = cs.fetchone()
	if result:
		basin_id, year, rainfall = result
		return StationYearAmount(
			basin_id=basin_id,
			year=year,
			rainfall=rainfall
		)
	else:
		raise HTTPException(status_code=404, detail="Basin not found")
	

	