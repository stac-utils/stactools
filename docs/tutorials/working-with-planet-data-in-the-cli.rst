Working with Planet Data in the CLI
###################################

In this tutorial, we'll use the stactools CLI to work with Planet data. We'll convert two Planet orders into STACs,
merge the STACs, modify their layout, and browse results using the ``stac browse`` command.

If you'd like to use the Python library functionality, see the :ref:`tutorial notebook </tutorials/working-withplanet-data.ipynb>` that performs the same actions, but in Python.

You'll need the `stactools_planet` and `stactools_browse` packages to follow along. You can install these with:

.. code-block:: console

   > pip install stactools[planet,browse]

If you're using a cloned repository to run this tutorial, you can use ``scripts/stac`` wherever ``stac`` is used. Remember to run ``scripts/update`` to ensure all the necessary dependencies are installed.

Prerequisites
=============

For this tutorial we'll be ordering data from Planet's API. You'll need an account with access to the orders API.
The tutorial will use data that is available in the `Developer Trial Program <https://developers.planet.com/devtrial/>`_, so sign up there if you don't already have an account - and let them know you are creating STACs!

We'll assume that you've run ``planet init`` to log in and store your API key in local configuration.

You'll need the `planet CLI <https://planetlabs.github.io/planet-client-python/cli/index.html>`_ installed, as well as the ``stactools_planet`` and ``stactools_browse`` package.

You'll also need Docker installed to be able to use the ``stac browse`` command.

Ordering from Planet
====================

We'll use IDs that are generated from a search that we performed in the :ref:`tutorial notebook </tutorials/working-withplanet-data.ipynb>`, so see that for a reference of how those searches were performed. The IDs are for 8 items over a part of southern Myanmar. Let's store those IDs in environment variables:

.. code-block:: console

   > export TUTORIAL_ORDER_IDS=20190111_034458_0f3f,20190111_034459_0f3f,20190111_034457_0f3f,20190111_033800_0f46,20190111_033759_0f46,20190109_034416_103d,20190109_034415_103d,20190109_034414_103d

We'll need to specify a tool to ensure our GeoTIFFs are delivered as COGs. To do so, create a JSON file with the following content at ``tools.json``

.. code-block:: javascript

   [
        {
          "file_format": {
            "format": "COG"
          }
        }
   ]

The data we will be ordering will be from 3-band and 4-band PlanetScope Scenes.

Ordering visual products
~~~~~~~~~~~~~~~~~~~~~~~~

Now we can use the planet CLI to order visual PSScene3Band bundles for these items:

.. code-block:: console

   > planet orders create --name "Test order - visual" \
   --id ${TUTORIAL_ORDER_IDS} \
   --bundle visual --item-type psscene3band --zip order --email --tools tools.json

Grab the ``"id"`` value from the JSON response, and store it in an environment variable ``ORDER_ID`` (or replace instances of that variable with the ID in the commands below).

We can check the status of our order with:

.. code-block:: console

   > planet orders get ${ORDER_ID}

Notice the "state" property in the response. When that reads "success", the order will be ready to download.

We'll make a directory to store the results in, and then download our order:

.. code-block:: console

   > mkdir -p order-downloads/visual
   > planet orders download --dest order-downloads/visual ${ORDER_ID}

We can then unzip our order:

.. code-block:: console

   > cd order-downloads/visual
   > unzip *.zip

If the unzipping process asks you to override ``manifest.json``, select yes.

Ordering analytic products
~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll order PSScene4Band analytic surface reflectance bundles next by performing the same actions as above, with the same items, but specifying by replacing the ``bundle`` to ``analytic_sr`` and ``item-type`` to ``psscene4band`` in the order:

.. code-block:: console

   > planet orders create --name "Test order - analytic" \
   --id ${TUTORIAL_ORDER_IDS} \
   --bundle analytic_sr --item-type psscene4band --zip order --email --tools tools.json

Once finished, download the results of that order and unzip to ``order-downloads/analytic`` similar to how we did above.

Creating STACs
==============

Back at the root directory where we started, we can create STACs of these orders with the ``planet convert-order`` command:

.. code-block:: console

   > stac planet convert-order \
       order-downloads/visual/manifest.json \
       planet-stacs/visual \
       planet-data \
       "A planet order converted to STAC" \
       --assets copy \
       --title "Planet data over S Myanmar"

We use the ``--assets copy`` option to copy our files alongside of the STAC Items that are created so that ``stac browse`` can have proper access to them when serving out tiles on the map.

You can do the same thing with the analytics order - create a STAC at ``planet-stacs/analytics``.

Browsing the STACs
==================

You can start a stac-browser to see our order STAC by using the ``stac browse`` command:

.. code-block:: console

   > stac browse planet-stacs/visual/collection.json


After the docker containers fire up and the serere starts, go to http://localhost:1234 to see your STAC.

You can quit out of the browser with Ctrl+C.

Note that if you are switching between browsing different catalogs, your browser might cache results an produce incorrectr results. If this happens, try hard refreshing or disabling caching.

Updating the STACs
==================

Adding assets to existing items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both the analytic and visual catalogs contain the same items, and we may want to combine our orders into one single STAC. Additionally, if you create a STAC and then order new data later, you may want to merge in that new order data into the existing STAC.

We'll merge in the items from the analytic STAC into the visual STAC to create a single collection using:

.. code-block:: console

   > stac merge planet-stacs/analytic/collection.json planet-stacs/visual/collection.json --move-assets --ignore-conflicts

The ``--ignore-conflicts`` flag will cause stactools to avoid replacing assets if an asset key already exists (e.g. the metadata JSON for the Planet items), and will avoid overwriting files that already exist when moving assets around.

We can use ``stac browse`` to see our newly merged catalog to see that the analytic assets are now in the items.

Adding another order to our collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can use ``stac merge`` to add another order to our collection. The following IDs are based on a similar area as our original orders, but spread through September 2018 to March 2019:

.. code-block:: console

   > export TUTORIAL_ORDER_IDS=20180924_034401_0f3f,20181025_034420_0f4e,20181125_034649_0f28,20181227_034225_0f2b,20190119_034511_1035,20190212_033542_1054,20190322_034910_0f12

Save an order with those IDs to ``order-downloads/range`` and generate a STAC from if using the methods above. The STAC of that order should be at ``planet-stacs/range/collection.json``

We can copy the visual catalog to a final catalog, and merge in the time range order like this:

.. code-block:: console

   > stac copy planet-stacs/visual/collection.json planet-stacs/final
   > stac merge planet-stacs/range/collection.json planet-stacs/visual/collection.json --ignore-conflicts

Notice we are not moving assets around just yet. We'll reorganize the STAC first before moving large files around.


Changing the layout
===================

Let's look at some info about our stac:

.. code-block:: console

   > stac info planet-stacs/final/collection.json
   > stac describe planet-stacs/final/collection.json

For a small STAC, this many items in a single collect may be OK. But as we add orders to this STAC, we may want to organize things differently.

We can create subcatalogs that are based on date with the following command:

.. code-block:: console

   > stac layout --create-subcatalogs --move-assets planet-stacs/final/collection.json "{year}/{month}"

This creates subcatalogs and organizes each item into a subcatalog based on the properties of the item. Here we use the year and month of the item's datetime to create two levels of subcatalogs. Now if we run:

.. code-block:: console

   > stac describe planet-stacs/final/collection.json

We can see the modified layout.

And we're done! We can fire up stac-browser to look at our final catalog, organized by year and month, generated and updated from multiple orders.

.. code-block:: console

   > stac browse planet-stacs/final/collection.json
