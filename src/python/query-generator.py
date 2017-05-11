#!/usr/local/bin/python

# query-generator.py NUM_QUERIES MAX_PARTITIONS NUM_TILES OUTPUT_FILE

import sys
import random
import math

def getRowOrderSequence(zStart, zEnd, maxPartitions):
    rowOrderTiles = []

    for index in range(zStart, zEnd):
        # z = "{0:b}".format(index)
        z = format(index-1, "08b")
        print("<<<# " + z)

        index = 0
        strRow = ""
        strCol = ""

        if len(z) % 2 != 0:
            z += "0"

        while index < len(z):
            strRow = strRow + z[index]
            strCol = strCol + z[index+1]
            index += 2

        limit = int(math.sqrt(maxPartitions))
        row = int(strRow, 2)
        col = int(strCol, 2)

        finalIndex = (limit * row) + col
        rowOrderTiles.append(finalIndex)

    return rowOrderTiles

def getRowOrderWHEREfromSequence(indeces, attribute):
    whereStatement = "WHERE "
    lastIndex = indeces[-1]
    for index in indeces:
        cmp = " {} = {} ".format(attribute, index)
        whereStatement += cmp

        if index != lastIndex:
            whereStatement += " OR "

    return whereStatement

def saveQueries(queries, fileName, numTiles):
    output = open(fileName, "w")
    output.write("val queries = List(")
    lastQuery = queries[-1]
    for query in queries:
        output.write("(\"{}\", {})".format(query, numTiles))

        if query != lastQuery:
            output.write(",")

        output.write("\n")

    output.write(")\n")
    output.close()

# Arguments from user
NUM_QUERIES = int(sys.argv[1])
MAX_PARTITIONS = int(sys.argv[2])
NUM_TILES = int(sys.argv[3])
OUTPUT_FILE = sys.argv[4]

# Things to change
SELECT_ATTR = "imageBytes"
WHERE_ATTR = "partitionZIndex"
WHERE_RO_ATTR = "partitionIndex"
TABLE_NAME = "data"

SELECT_TEMPLATE = "SELECT {} FROM {} "
SEQUENCE_WHERE_TEMPLATE = "{} >= {} AND {} <= {}"
PIVOTS = []
QUERIES = []
RO_QUERIES = []
ROWORDER_TILES = []

select = SELECT_TEMPLATE.format(SELECT_ATTR, TABLE_NAME)

# We need a NUM_QUERIES random numbers from 1 to (MAX_PARTITIONS - NUM_TILES)
while len(PIVOTS) < NUM_QUERIES:
    randomNum = random.randint(1, (MAX_PARTITIONS - NUM_TILES))

    if randomNum not in PIVOTS:
        PIVOTS.append(randomNum)
        print(">> PROGRESS: {}/{}".format(len(PIVOTS), NUM_QUERIES))


print("\n>> GENERATING ZORDER QUERIES AND ROWORDER TILES")
for pivot in PIVOTS:
    where = SEQUENCE_WHERE_TEMPLATE.format(WHERE_ATTR, pivot, WHERE_ATTR, (pivot + NUM_TILES-1))
    query = "".join([select, where])

    QUERIES.append(query)
    ROWORDER_TILES.append(getRowOrderSequence(pivot, (pivot + NUM_TILES), MAX_PARTITIONS))

print("\n>> GENERATING ROWORDER QUERIES")
for pivots in ROWORDER_TILES:
    where = getRowOrderWHEREfromSequence(pivots, WHERE_RO_ATTR)
    query = "".join([select, where])
    RO_QUERIES.append(query)



# Write it as scala code for the zOrder queries
print("\n>> SAVING ZORDER QUERIES")
saveQueries(QUERIES, OUTPUT_FILE + ".zorder", NUM_TILES)

print("\n>> SAVING ROWORDER QUERIES")
saveQueries(RO_QUERIES, OUTPUT_FILE + ".roworder", NUM_TILES)
