\# TERRATIME 4D — Global Geology Pilot Report



\## 1. Objective



Conduct an initial geographically distributed geological data survey using the Macrostrat API to evaluate its usefulness for identifying potential Earth mission-analog environments.



\## 2. Data source



\- \*\*Source:\*\* Macrostrat geological database API

\- \*\*Endpoint:\*\* `https://macrostrat.org/api/v2/geologic\_units/map`

\- \*\*Query method:\*\* Latitude and longitude point queries

\- \*\*Initial sampling:\*\* 24 locations

\- \*\*Geographic sampling:\*\* Six latitude bands and four longitude regions



\## 3. Results



\- Locations queried: 24

\- Successful geological records retrieved: 25

\- Locations with at least one record: 11

\- Locations with zero records: 13



\## 4. Geological observations



The pilot identified several types of geological information:



\- Ancient crystalline metamorphic rocks

\- Sedimentary rocks and deposits

\- Cretaceous and Jurassic geological formations

\- Arctic sedimentary formations

\- Ice-related geological records

\- Water and lake-related records



Examples include:



\- Cell 253: Archean–Paleoproterozoic crystalline metamorphic rocks.

\- Cell 1531: Neogene sedimentary deposits.

\- Cell 2395: Early Cretaceous sedimentary formations, including sandstone, siltstone and shale.

\- Cell 271: Phanerozoic ice.

\- Cell 1963: Water records and lake sediments.



\## 5. Source tracking



The collected records include:



\- `cell\_id`

\- Latitude and longitude

\- Geological unit name

\- Lithology

\- Geological age

\- Geological period

\- `map\_id`

\- `source\_id`



Multiple geological records can occur at one coordinate because different geological maps and sources may overlap.



\## 6. Output files



Location:



`data/processed/global\_geology/`



Files:



\- `global\_geology\_cell\_status.csv` — query status and record counts for each sampled location.

\- `global\_geology\_records.csv` — geological records and their source identifiers.



\## 7. Limitations



1\. This is an initial pilot, not a complete global geological survey.

2\. The 24 sample points do not represent every land region.

3\. A zero-record response does not establish that geology is absent.

4\. Water and ice records must be distinguished from exposed terrestrial geology.

5\. Geological records require source verification and spatial validation.

6\. These observations do not yet establish confirmed lunar or Martian analog sites.



\## 8. Next research priorities



1\. Improve global sampling and land-versus-water classification.

2\. Expand geological data collection beyond the 24 pilot locations.

3\. Preserve source references, map scales and API licensing information.

4\. Combine geology with elevation, terrain, temperature, ice and environmental datasets.

5\. Identify and validate potential Earth mission-analog candidates.



\## 9. Conclusion



The initial Macrostrat pilot successfully retrieved 25 geological records across 11 sampled locations. It demonstrates that automated geological data collection can support the TERRATIME 4D project.



Further global sampling, data-quality checks and environmental comparisons are required before identifying scientifically defensible mission-analog candidates.

