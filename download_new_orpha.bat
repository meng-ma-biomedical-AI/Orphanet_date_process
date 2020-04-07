set lang=(cs,de,en,es,fr,it,nl,pl,pt)

for %L in %lang% DO (curl -get http://www.orphadata.org/data/xml/%L_product1.xml > ./product1/%L_product1.xml)

for %L in %lang% DO (curl -get http://www.orphadata.org/data/xml/%L_product4.xml > ./product4/%L_product4.xml)

curl -get http://www.orphadata.org/data/xml/en_product6.xml > ./product6/en_product6.xml

for %L in %lang% DO (curl -get http://www.orphadata.org/data/xml/%L_product9_ages.xml > ./product9/%L_product9_ages.xml)

for %L in %lang% DO (curl -get http://www.orphadata.org/data/xml/%L_product9_prev.xml > ./product9/%L_product9_prev.xml)


"NOT USEFULL"

for %f in (146,147,148,149,150,152,156,181,182,183,184,185,186,187,188,189,193,194,195,196,197,198,199,200,201,202,203,204,205,209,211,212,216,229,231,233) DO (curl -get http://www.orphadata.org/data/xml/en_product3_%f.xml > ./product3/en_product3_%f.xml)