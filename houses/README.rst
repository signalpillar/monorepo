Using https://www.getthedata.com/open-postcode-geo-api I converted all the
postcodes to coordinates

Another cool https://postcodes.io/

.. code::

    poetry run python houses addofsted


07 Dec
------
- [x] Fix school rating rendering by colour.
- [ ] Not all ofsted reports are present, need to query ofsted site on `demand
  <https://reports.ofsted.gov.uk/provider/27/133444>_`.

06 Dec
------
- [ ] https://pypi.org/project/geopy/
  https://towardsdatascience.com/heres-how-to-calculate-distance-between-2-geolocations-in-python-93ecab5bbba4


I need to find places where I am interested to live in.

Using longon datastore to pick the borough

https://londondatastore-upload.s3.amazonaws.com/instant-atlas/borough-profiles/atlas.html

- [x] downloaded atlas.xlsx file from `gov
  <https://data.london.gov.uk/dataset/london-borough-profiles>_` site
- [x] `ofsted reports <https://public.tableau.com/views/DataViewGetTheData/Getthedata?:showVizHome=no>_`


29 Nov
------
Created zoopla dev account and got key.
Simple client to get listings by ZIP code.
I am going to render property on map.

28 Nov
------
I got all scools clustered using k-means algo for London.
Trying to render cluster in Jupyter notebook using `folium`_

folium_: https://python-visualization.github.io/folium/quickstart.html

I got schools rendered on map.
