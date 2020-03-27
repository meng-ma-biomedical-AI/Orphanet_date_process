set lang=(cs,de,en,es,fr,it,nl,pl,pt)

for %L in %lang% DO (curl -get http://www.orphadata.org/data/NEW_ORPHADATA_PRODUCTS/%L_product1.xml > ./%L_product1.xml)

for %L in %lang% DO (curl -get http://www.orphadata.org/data/NEW_ORPHADATA_PRODUCTS/%L_product4.xml > ./%L_product4.xml)

curl -get http://www.orphadata.org/data/NEW_ORPHADATA_PRODUCTS/en_product6.xml > ./en_product6.xml

for %L in %lang% DO (curl -get http://www.orphadata.org/data/NEW_ORPHADATA_PRODUCTS/%L_product9_ages.xml > ./%L_product9_ages.xml)

for %L in %lang% DO (curl -get http://www.orphadata.org/data/NEW_ORPHADATA_PRODUCTS/%L_product9_prev.xml > ./%L_product9_prev.xml)


NOT USEFULL

for /L %f in (146,1,150) DO (curl -get http://www.orphadata.org/data/NEW_ORPHADATA_PRODUCTS/en_product3_%f%.xml > ./en_product3_%f%.xml)