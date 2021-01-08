Scenario Generator: Proximity Based
===================================

Summary
-------

The proximity-based scenario generator creates a set of contrasting land
use change maps that convert habitat in different spatial patterns. The
user determines which habitat can be converted and what they are
converted to, as well as type of pattern, based on proximity to the edge
of a focal habitat. In this manner, an array of land-use change patterns
can be generated, including pasture encroaching into forest from the
forest edge, agriculture expanding from currently cropped areas, forest
fragmentation, and many others. The resulting land-use maps can then be
used as inputs to InVEST models, or other models for biodiversity or
ecosystem services that are responsive to land use change.

Introduction
------------

In order to understand the change in biodiversity and ecosystem services
(BES) resulting from change in land-use, it is often helpful to start
with a scenario or a set of scenarios that exhibit different types of
land-use change. Because many of the relationships between landscapes
and BES are spatially-explicit, a different pattern of habitat
conversion for the same total area of habitat converted can lead to very
different impacts on BES. This proximity-based scenario generator
creates different patterns of conversion according to user inputs
designating focal habitat and converted habitat, in contrast to but
potentially complementing the InVEST rule-based scenario generator that
creates maps of land-use change according to user-assigned probabilities
that certain transitions will occur. Thus, the intent of the InVEST
proximity-based scenario generator is not to forecast actual predicted
patterns of expansion, but rather to develop different patterns of land
use change in order to examine the relationship between land-use change
and BES, and how the relationship may differ depending on land use
change assumptions.

The model
---------

The tool can generate two scenarios at once (nearest to the edge and
farthest from the edge of a focal habitat), for a conversion to
particular habitat type for a given area. To convert to different
habitat types, different habitat amounts, or to designate different
focal habitats or converted habitats, the tool can be run multiple times
in sequence.

How it works
~~~~~~~~~~~~

Three types of landcover must be defined: 1) *Focal* *landcover* is the
landcover(s) that set the proximity rules from which the scenarios will
be determined. The scenario generator will convert habitat from the edge
or toward the edge of patches of these types of landcover. This does not
mean it will convert these land-covers, only that it will measure
distance to or from the edges in designating where the conversion will
happen. 2) *Convertible landcover* is the landcover(s) that can be
converted. These could be the same as the focal landcover(s), a subset,
or completely different. 3) *Replacement landcover* is the landcover
type to which the convertible landcovers will be converted. This can
only be one landcover type per model run.

Two scenarios can then be run at a time: 1) *Nearest to edge* means that
convertible landcover types closest to the edges of focal landcovers
will be converted to the replacement landcover. 2) *Farthest from edge*
means that convertible landcover types furthest from the edges of focal
landcover types will be converted to the replacement landcover. If this
scenario is chosen, the user can designate in how many steps the
conversion should occur. This is relevant if the focal landcover is the
same as the convertible land cover because the conversion of the focal
landcover will create new edges and hence will affect the distance
calculated from the edge of that landcover. If desired, the conversion
can occur in several steps, each time converting the farthest from the
edge of the focal landcover, causing a fragmentary pattern.

Below are some examples of the types of scenarios that can be generated
by manipulating these basic inputs, using the land-cover in the sample
data that ship with this model. This landcover is from MODIS, using the
UMD classification (Friedl et al. 2011), which follows the following
scheme: 1 – Evergreen needleleaf forest; 2 – Evergreen broadleaf forest;
3 – Deciduous needleleaf forest; 4 – Deciduous broadleaf forest; 5 –
Mixed forest; 6 – Closed shrublands; 7 – Open shrublands; 8 – Woody
savannas; 9 – Savannas; 10 – Grasslands; 12 – Croplands; 13 – Urban and
built-up; 16 – Barren or sparsely vegetated.

**Expand agriculture from forest edge inwards:**

focal landcover codes: 1 2 3 4 5

convertible landcover codes: 1 2 3 4 5

replacement landcover code: 12

check "Convert From Edge"

number of steps toward conversion: 1

**Expand agriculture from forest core outwards**:

focal landcover codes: 1 2 3 4 5

convertible landcover codes: 1 2 3 4 5

replacement landcover code: 12

check "Convert Toward Edge"

number of steps toward conversion: 1

**Expand agriculture by fragmenting forest:**

focal landcover codes: 1 2 3 4 5

convertible landcover codes: 1 2 3 4 5

replacement landcover code: 12

check "Convert Toward Edge"

number of steps toward conversion: 10 (or as many steps as desired; the
more steps, the more finely fragmented it will be and the longer the
simulation will take)

**Expand pasture into forest nearest to existing agriculture:**

focal landcover codes: 12

convertible landcover codes: 1 2 3 4 5

replacement landcover code: 10

check "Convert From Edge"

number of steps toward conversion: 1

Data needs
----------

The only required input data to run the proximity-based scenario
generator is a base land-use/land-cover map and user-defined land cover
codes pertaining to this base map to designate how the scenarios should
be computed.

1. Base land-use/cover map (required). This is the map that will be
   modified in the generation of the desired scenarios. All pixels in
   this map (that overlap with the area of interest, if included) other
   than the pixels that are converted will remain the same.

..

   Name: file can be named anything (scenario_proximity_lulc.tif in the
   sample data)

   Format: standard GIS raster file (e.g., ESRI GRID or IMG), with a
   column labeled ‘value’ that designates the LULC class code for each
   cell (integers only; e.g., 1 for forest, 10 for grassland, etc.)

2. AOI – Area of Interest (optional). If change is only desired in a
   subregion of the broader land-use/land-cover map, the user may
   designate this area of interest. Prior to scenario generation, the
   map will be clipped to the extent of this vector.

   Name: file can be named anything (scenario_proximity_aoi.shp in the
   sample data)

   Format: vector (polygon) file

3. Max area to convert (ha): enter the maximum numbers of hectares to be
   converted to agriculture. This is the maximum because due to the
   discretization of area of pixels, the number of pixels closest to but
   not exceeding this number will be converted.

4. Focal Landcover Codes: enter the LULC code(s) for the land cover
   types from which distance from edge should be calculated. If multiple
   values, they should be separated by spaces.

5. Convertible Landcover Codes: enter the LULC code(s) for the land
   cover types that are allowed to be converted to agriculture in the
   simulation. If multiple values, they should be separated by spaces.

6. Replacement Landcover Code: enter an integer that corresponds to the
   LULC code to which habitat will be converted. If there are multiple
   LULC types that are of interest for conversion, this tool should be
   run in sequence, choosing one type of conversion each time. A new
   code may be introduced if it is a novel land-use for the region or if
   it is desirable to track the expanded land-use as separate from
   historic land-use.

7. Check boxes: types of scenarios to generate

   i.  Convert farthest from edge: land cover type(s) designated as
       “convertible” that are farthest from the edge of any land cover
       type designated as “focal” will be converted. Convertible land
       covers and habitat of interest land-covers may be the same, or a
       subset of one another, or they can be different. If they are the
       same, the number of steps for conversion should be specified,
       because the conversion of habitat within the focal land cover
       will create new habitat edge, resulting in a completely different
       pattern of conversion depending on how many steps are chosen.

   ii. Convert nearest to edge: land cover type(s) designated as
       “convertible” that are nearest to the edge of any land cover type
       designated as “focal” will be converted. As for the previous
       scenario, convertible land covers and habitat of interest
       land-covers may be the same, or a subset of one another, or they
       can be different.

8. Number of Steps in Conversion: enter an integer for the number of
   steps the simulation should take to fragment the habitat of interest
   in the fragmentation scenario. Entering a 1 means that all of the
   habitat conversion will occur in the center of the patch of the
   habitat of interest. Entering 10 will be fragmented according to a
   pattern of sequentially converting the pixels furthest from the edge
   of that habitat, over the number of steps specified by the user.

Running the model
-----------------

The model is available as a standalone application accessible from the
install directory of InVEST (under the subdirectory
invest-3_x86/invest_scenario_gen_proximity.bat).

Advanced Usage
~~~~~~~~~~~~~~

This model supports avoided re-computation. This means the model will
detect intermediate and final results from a previous run in the
specified workspace and it will avoid re-calculating any outputs that
are identical to the previous run. This can save significant processing
time for successive runs when only some input parameters have changed.

Viewing Output from the Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Upon successful completion of the model, a file explorer window will
open to the output workspace specified in the model run. This directory
contains an output folder holding files generated by this model. Those
files can be viewed in any GIS tool such as ArcGIS, or QGIS. These files
are described below in Section Interpreting Results.

Interpreting Results
--------------------

Final Results
~~~~~~~~~~~~~

Final results are found in the \ *Workspace* folder within the specified
for this module.

-  **InVEST….log…txt:** Each time the model is run, a text (.txt) file
   will appear in the \ *Output* folder. The file will list the
   parameter values for that run and will be named according to the
   model, the date and time, and the suffix.

-  **nearest_to_edge \_<suffix>.tif: LULC raster for the scenario of
   conversion nearest to the edge of the focal habitat**

-  **farthest_from_edge_<suffix>.tif: LULC raster for the scenario of
   conversion farthest from the edge of the focal habitat**

-  **nearest_to__edge_<suffix>.csv: table listing the area (in hectares)
   and number of pixels for different land cover types converted for the
   scenario of conversion nearest to the edge of the focal habitat**

-  **farthest_from_edge \_<suffix>.csv: table listing the area (in
   hectares) and number of pixels for different land cover types
   converted for the scenario of conversion nearest to the edge of the
   focal habitat**

Intermediate Results
~~~~~~~~~~~~~~~~~~~~

You may also want to examine the intermediate results. These files can
help determine the reasons for the patterns in the final results. They
are found in the \ *intermediate_outputs* folder within the
*Workspace* specified for this module.

-  **{farthest_from_/nearest_to}_edge_distance_<suffix>.tif**: This
      raster shows the distance (in number of pixels) of each pixel to
      the nearest edge of the focal landcover.

-  **_tmp_work_tokens:** This directory stores metadata used internally
      to enable avoided re-computation.

Sample Script
-------------

The following script is provided to demonstrate how the scenarios
described in Section “How It Works” can be composed into a single script
that’s callable from the InVEST Python API::

        import natcap.invest.scenario_generator_proximity_based

        edge_args = {
            u'aoi_path': u'C:/Users/Rich/Documents/svn_repos/invest-sample-data/scenario_proximity/scenario_proximity_aoi.shp',
            u'area_to_convert': u'20000.0',
            u'base_lulc_path': u'C:/Users/Rich/Documents/svn_repos/invest-sample-data/scenario_proximity/scenario_proximity_lulc.tif',
            u'convert_farthest_from_edge': False,
            u'convert_nearest_to_edge': True,
            u'convertible_landcover_codes': u'1 2 3 4 5',
            u'focal_landcover_codes': u'1 2 3 4 5',
            u'n_fragmentation_steps': u'1',
            u'replacment_lucode': u'12',
            u'results_suffix': 'edge',
            u'workspace_dir': u'C:\\Users\\Rich/Documents/scenario_proximity_workspace',
        }

        core_args = {
            u'aoi_path': u'C:/Users/Rich/Documents/svn_repos/invest-sample-data/scenario_proximity/scenario_proximity_aoi.shp',
            u'area_to_convert': u'20000.0',
            u'base_lulc_path': u'C:/Users/Rich/Documents/svn_repos/invest-sample-data/scenario_proximity/scenario_proximity_lulc.tif',
            u'convert_farthest_from_edge': True,
            u'convert_nearest_to_edge': False,
            u'convertible_landcover_codes': u'1 2 3 4 5',
            u'focal_landcover_codes': u'1 2 3 4 5',
            u'n_fragmentation_steps': u'1',
            u'replacment_lucode': u'12',
            u'results_suffix': 'core',
            u'workspace_dir': u'C:\\Users\\Rich/Documents/scenario_proximity_workspace',
        }

        frag_args = {
            u'aoi_path': u'C:/Users/Rich/Documents/svn_repos/invest-sample-data/scenario_proximity/scenario_proximity_aoi.shp',
            u'area_to_convert': u'20000.0',
            u'base_lulc_path': u'C:/Users/Rich/Documents/svn_repos/invest-sample-data/scenario_proximity/scenario_proximity_lulc.tif',
            u'convert_farthest_from_edge': True,
            u'convert_nearest_to_edge': False,
            u'convertible_landcover_codes': u'1 2 3 4 5',
            u'focal_landcover_codes': u'1 2 3 4 5',
            u'n_fragmentation_steps': u'10',
            u'replacment_lucode': u'12',
            u'results_suffix': 'frag',
            u'workspace_dir': u'C:\\Users\\Rich/Documents/scenario_proximity_workspace',
        }

        ag_args = {
            u'aoi_path': u'C:/Users/Rich/Documents/svn_repos/invest-sample-data/scenario_proximity/scenario_proximity_aoi.shp',
            u'area_to_convert': u'20000.0',
            u'base_lulc_path': u'C:/Users/Rich/Documents/svn_repos/invest-sample-data/scenario_proximity/scenario_proximity_lulc.tif',
            u'convert_farthest_from_edge': False,
            u'convert_nearest_to_edge': True,
            u'convertible_landcover_codes': u'12',
            u'focal_landcover_codes': u'1 2 3 4 5',
            u'n_fragmentation_steps': u'1',
            u'replacment_lucode': u'12',
            u'results_suffix': 'ag',
            u'workspace_dir': u'C:\\Users\\Rich/Documents/scenario_proximity_workspace',
        }
        if __name__ == '__main__':
            natcap.invest.scenario_generator_proximity_based.execute(edge_args)
            natcap.invest.scenario_generator_proximity_based.execute(core_args)
            natcap.invest.scenario_generator_proximity_based.execute(frag_args)
            natcap.invest.scenario_generator_proximity_based.execute(ag_args)
