#!/usr/bin/env python

import grass.script as gscript
import os


liConfigFile = "C:\\Users\\PTABRIZ\\AppData\\Roaming\\GRASS7\\r.li\\config_7"
metricPath = "C:\\Users\\PTABRIZ\\AppData\\Roaming\\GRASS7\\r.li\\output\\"
outFileName = "D:\\Dix_study\\Output\\metricout_large_data3.txt"


def viewshed(file):
    coordFile = open(file, "r")
    lineCount = sum(1 for _ in coordFile)
    coordFile.seek(0)
    outFile = open(outFileName, "a")
    outFile.write(Makeheader())

    selectList = [
        2,
        6,
        11,
        14,
        34,
        38,
        45,
        48,
        62,
        63,
        79,
        83,
        87,
        111,
        129,
        132,
        138,
        142,
        194,
        196,
        210,
        224,
        225,
        275,
    ]

    for counter, line in enumerate(coordFile.readlines()):
        Xcoord = split = line.split(",")[0]
        Ycoord = split = line.split(",")[1]
        index = line.split(",")[2]

        luse_raster = "Landcover_final"
        DHM = "DHM_final"
        in_raster = "DSM"

        observerRaster = "observer_raster"
        DHM_clump = "DHM_clump"
        out_viewshed = "viewshed" + str(int(index))
        out_landuse = "luse_out_" + str(int(index))
        out_binary = "binary" + str(int(index))
        out_neighbor = "neighbor" + str(int(index))
        out_clump = "clump" + str(int(index))
        out_clumpNear = "near_clump" + str(int(index))
        out_horizontal = "hor" + str(int(index))
        out_observerCell = "obcell" + str(int(index))
        out_distance = "distance" + str(int(index))
        out_relief = "relief" + str(int(index))
        out_skyline = "skyline" + str(int(index))

        SDI = "li_shannon" + str(int(index))
        ED = "li_ED" + str(int(index))
        Nump = "li_Nump" + str(int(index))
        MSI = "li_MSI" + str(int(index))
        PSCoV = "li_Pscov" + str(int(index))

        out_univar = "D:\\DIX_GIS_Data\\Viewshed_project\\data\\{0}_stat.txt".format(
            out_viewshed
        )
        out_cat = "D:\\DIX_GIS_Data\\Viewshed_project\\data\\{0}_cat.txt".format(
            out_viewshed
        )
        out_object = "D:\\DIX_GIS_Data\\Viewshed_project\\data\\{0}_obj.txt".format(
            out_viewshed
        )
        out_obs = "D:\\DIX_GIS_Data\\Viewshed_project\\data\\{0}_obs.txt".format(
            out_viewshed
        )

        out_SDI = "{0}_SDI.txt".format(out_viewshed)
        out_ED = "{0}_ED.txt".format(out_viewshed)
        out_NUMP = "{0}_NUMP.txt".format(out_viewshed)
        out_MSI = "{0}_MSI.txt".format(out_viewshed)
        out_PSCOV = "{0}_PSCoV.txt".format(out_viewshed)
        out_PD = "{0}_PD.txt".format(out_viewshed)
        out_RCH = "{0}_RCH.txt".format(out_viewshed)
        out_mps = "{0}_MPS.txt".format(out_viewshed)

        out_MSI_hor = "{0}_MSI_hor.txt".format(out_viewshed)
        MSI_hor_file = os.path.join(metricPath, out_MSI_hor)

        # this condition is used for testing purposes
        # eg. if int(index) == 3 computes the viewshed metrics only the third point

        if int(index):

            #### Visibility Maps ####
            try:
                # 1. compute viewshed #
                gscript.run_command(
                    "r.viewshed",
                    input=in_raster,
                    output=out_viewshed,
                    coordinates=[Xcoord, Ycoord],
                    observer_elevation=1.65,
                    target_elevation=0.5,
                    memory=32000,
                    overwrite=True,
                    max_distance=3000,
                    flags="e",
                )
                # 2. make binary viewsheds, compute focal statistics, compute object clumps #
                gscript.run_command(
                    "r.mapcalc",
                    expression="{0}=if({1},1,0)".format(out_binary, out_viewshed),
                    overwrite=True,
                )
                # 3. Create horizontal surface using DHM and Binary viewshed ##
                gscript.run_command(
                    "r.mapcalc",
                    expression="{0}=if(isnull({1}),{2},null())".format(
                        out_horizontal, DHM, out_binary
                    ),
                    overwrite=True,
                )
                ## 4.create distance raster for depth
                gscript.run_command(
                    "r.grow.distance",
                    input=out_observerCell,
                    distance=out_distance,
                    overwrite=True,
                )
                # 5. Vertical viewsheds (skyline and releif)
                ## intersect the elevation_diffrence viewshed with the DHM
                gscript.run_command(
                    "r.mapcalc",
                    expression="{0}=if(isnull({1}),{2},null())".format(
                        out_relief, DHM, out_viewshed
                    ),
                    overwrite=True,
                )
                ## intersect the elevation_diffrence viewshed with the DHM
                gscript.run_command(
                    "r.mapcalc",
                    expression="{0}=if({1},{2},null())".format(
                        out_skyline, DHM, out_viewshed
                    ),
                    overwrite=True,
                )

            except:
                #
                print "There was a problem in the process of computing stats for viewshed {0}".format(
                    index
                )

            #### Composition rasters  ####
            try:

                # 8. Overlay landcover with viewshed and inherit the classification #
                gscript.run_command(
                    "r.mapcalc",
                    expression="{0}=if({1},{2},null())".format(
                        out_landuse, out_viewshed, luse_raster
                    ),
                    overwrite=True,
                )
                gscript.run_command("r.category", map=out_landuse, raster=luse_raster)
                gscript.run_command("r.colors", map=out_landuse, raster=luse_raster)

                # 9. landscape metrics
                gscript.run_command(
                    "r.li.shannon",
                    input=out_landuse,
                    output=out_SDI,
                    config=liConfigFile,
                    overwrite=True,
                )
                gscript.run_command(
                    "r.li.edgedensity",
                    input=out_landuse,
                    output=out_ED,
                    config=liConfigFile,
                    overwrite=True,
                )
                gscript.run_command(
                    "r.li.patchnum",
                    input=out_landuse,
                    output=out_NUMP,
                    config=liConfigFile,
                    overwrite=True,
                )
                gscript.run_command(
                    "r.li.shape",
                    input=out_landuse,
                    output=out_MSI,
                    config=liConfigFile,
                    overwrite=True,
                )
                gscript.run_command(
                    "r.li.padcv",
                    input=out_landuse,
                    output=out_PSCOV,
                    config=liConfigFile,
                    overwrite=True,
                )
                gscript.run_command(
                    "r.li.mps",
                    input=out_landuse,
                    output=out_mps,
                    config=liConfigFile,
                    overwrite=True,
                )
                gscript.run_command(
                    "r.li.patchdensity",
                    input=out_landuse,
                    output=out_PD,
                    config=liConfigFile,
                    overwrite=True,
                )
                gscript.run_command(
                    "r.li.richness",
                    input=out_landuse,
                    output=out_RCH,
                    config=liConfigFile,
                    overwrite=True,
                )
                gscript.run_command(
                    "r.li.shape",
                    input=out_horizontal,
                    output=out_MSI_hor,
                    config=liConfigFile,
                    overwrite=True,
                )

                print "landscape metrics exported"

            except:
                print "There was a problem in the process of computing composition metrics for viewshed {0}".format(
                    index
                )
            try:

                # report statistics
                stat_luse = gscript.parse_command(
                    "r.univar", map=out_landuse, flags="g", overwrite=True
                )
                stat_hor = gscript.parse_command(
                    "r.univar", map=out_horizontal, flags="g", overwrite=True
                )
                stat_Depth = gscript.parse_command(
                    "r.univar", map=out_distance, flags="ge", overwrite=True
                )
                stat_relief = gscript.parse_command(
                    "r.univar", map=out_relief, flags="g", overwrite=True
                )
                stat_skyline = gscript.parse_command(
                    "r.univar", map=out_skyline, flags="g", overwrite=True
                )

                totVertical = stat_skyline["n"]
                totArea = stat_luse["n"]
                extent = stat_luse["sum"]

                horizontal = stat_hor["sum"]
                depth = str(int(float(str(stat_Depth["max"]))))
                relief = str(round(float(str(stat_relief["stddev"])), 2))
                skyline = str(round(float(str(stat_skyline["stddev"])), 2))
                b = str(open(MSI_hor_file).readlines())
                MSI_hor = round(float(str(b.split("|")[1])[:-4]), 2)

                # Compositional metrics"
                gscript.parse_command(
                    "r.stats",
                    input=out_landuse,
                    output=out_cat,
                    flags="acl",
                    separator="comma",
                    overwrite=True,
                )

                compMetrics = composition(out_cat)
                herbaceous = ((float(compMetrics["71"])) / int(totArea)) * 100
                grass = (
                    (float(compMetrics["85"]) + float(compMetrics["51"])) / int(totArea)
                ) * 100

                building = (
                    (float(compMetrics["20"]) + float(compMetrics["21"])) / int(totArea)
                ) * 100
                paved = ((float(compMetrics["234"])) / int(totArea)) * 100
                decidous = ((float(compMetrics["41"])) / int(totArea)) * 100
                evergreen = ((float(compMetrics["42"])) / int(totArea)) * 100
                mixed = ((float(compMetrics["43"])) / int(totArea)) * 100

                herbaceous = str(round(herbaceous, 1))
                grass = str(round(grass, 1))

            except:
                print "There was a problem in the process of Composition metrics for viewshed {0}".format(
                    index
                )

            # Configuration metrics
            try:

                Shannon = str(metricsRead(out_SDI))
                Nump = str(metricsRead(out_NUMP))
                PatchDensity = str(metricsRead(out_PD))
                ED = str(metricsRead(out_ED))
                MSI = str(metricsRead(out_MSI))
                MPS = str(metricsRead(out_mps))

            except:

                print "Configuration metrics for the viewshed {0} resulted in error".format(
                    index
                )

            # write into the file #
            if outlier == 1:

                output = (
                    str(index).strip("\n")
                    + "\t"
                    + str(extent)
                    + "\t"
                    + str(depth)
                    + "\t"
                    + str(horizontal)
                    + "\t"
                    + str(MSI_hor)
                    + "\t"
                    + str(relief)
                    + "\t"
                    + str(skyline)
                    + "\t"
                    + Npatch
                    + "\t"
                    + Canopy
                    + "\t"
                    + Built
                    + "\t"
                    + herbaceous
                    + "\t"
                    + grass
                    + "\t"
                    + Shannon
                    + "\t"
                    + Nump
                    + "\t"
                    + PatchDensity
                    + "\t"
                    + ED
                    + "\t"
                    + MSI
                    + "\t"
                    + MPS
                    + "\n"
                )
            else:
                output = str(index) + "\t" + "outlier" + "\n"

            outFile.write(output)

    outFile.close()


def composition(filename):
    file = open(filename)
    luseCodeList = ["5", "20", "21", "41", "42", "43", "51", "71", "85", "234", "233"]
    luseAreaList = []
    luseAreaDic = {}

    for line in file.readlines():
        catSplit = line.split(",")
        luseIndex = catSplit[0]
        area = catSplit[2]
        for luseCode in luseCodeList:
            if luseCode == luseIndex:
                luseArea = area
                luseAreaDic[luseIndex] = luseArea

    for luseCode in luseCodeList:
        if luseCode in luseAreaDic.keys():
            luseAreaList.append(luseAreaDic[luseCode])
        else:
            luseAreaDic[luseCode] = 0

    return luseAreaDic


def getclassNumbers(raster, output):

    gscript.parse_command(
        "r.object.geometry",
        input=raster,
        separator="comma",
        flags="m",
        output=output,
        overwrite=True,
    )
    classList = []
    for a in open(output, "r").readlines()[1:]:

        line = a.split(",")
        cat = line[0]
        area = line[1]
        if float(area) and float(area) >= 1:
            classList.append(cat)

    return classList


def metricsRead(fileName):
    outFile = os.path.join(metricPath, fileName)
    b = str(open(outFile).readlines())
    out = round(float(str(b.split("|")[1])[:-4]), 3)

    return out


def Makeheader():
    header = (
        "Index"
        + "\t"
        + "extent"
        + "\t"
        + "depth"
        + "\t"
        + "horizontal_surface"
        + "\t"
        + "viewdepth_variation"
        + "\t"
        + "relief"
        + "\t"
        + "skyline"
        + "\t"
        + "Npatch"
        + "\t"
        "Canopy_Percent"
        + "\t"
        + "Built_percent"
        + "\t"
        + "herbaceous"
        + "\t"
        + "grass"
        + "\t"
        + "Shannon"
        + "\t"
        + "Patch_no"
        + "\t"
        + "Patch_density"
        + "\t"
        + "Edge_density"
        + "\t"
        + "shape_index"
        + "\t"
        + "patch_size"
        + "\n"
    )
    return header


if __name__ == "__main__":
    viewshed("C:\\uses\\ptabriz\\documents\\GRASSDATA\\viewCoords.txt")
