package ar.edu.itba.ss

import io.github.oshai.kotlinlogging.KotlinLogging

class Grid(settings: Settings) {
    private val logger = KotlinLogging.logger {}

    private val rowSize = settings.gridSize
    val gridSize = settings.gridSizeSquared

    private val grid = IntArray(gridSize)

    init {
        for (i in grid.indices) {
            grid[i] = randomVote(settings).value
        }
    }

    fun forEach(action: (Vote) -> Unit) {
        grid.forEach { action(Vote.fromInt(it)!!) }
    }

    fun forEachRaw(action: (Int) -> Unit) {
        grid.forEach { action(it) }
    }

    fun sum() = grid.sum()

    fun get(column: Int, row: Int) = getByCoordinates(column, row, false)

    fun set(column: Int, row: Int, vote: Vote) {
        validateCoordinatesBoundaries(column, row)
        grid[row * rowSize + column] = vote.value
    }


    private fun getByCoordinates(column: Int, row: Int, periodic: Boolean): Vote {
        var mutableColumn = column
        var mutableRow = row
        if (periodic) {
            if (column < 0) {
                mutableColumn = rowSize - 1
            } else if (column >= rowSize) {
                mutableColumn = 0
            }

            if (row < 0) {
                mutableRow = rowSize - 1
            } else if (row >= rowSize) {
                mutableRow = 0
            }
        } else {
            validateCoordinatesBoundaries(column, row)
        }

        return if (grid[mutableRow * rowSize + mutableColumn] == Vote.LEFT_WING.value) {
            Vote.LEFT_WING
        } else {
            Vote.RIGHT_WING
        };
    }

    fun getNeighbors(column: Int, row: Int): List<Vote> {
        // Von Neumann neighbours
        validateCoordinatesBoundaries(column, row)
        return listOf(
            getByCoordinates(column, row - 1, true),
            getByCoordinates(column, row + 1, true),
            getByCoordinates(column - 1, row, true),
            getByCoordinates(column + 1, row, true),
        )
    }

    private fun validateCoordinatesBoundaries(column: Int, row: Int) {
        if (row !in 0..rowSize) {
            logger.error { "row index out of bounds: $row" }
            throw IndexOutOfBoundsException("row index out of bounds: $row")
        }
        if (column !in 0..rowSize) {
            logger.error { "column index out of bounds: $column" }
            throw IndexOutOfBoundsException("column index out of bounds: $column")
        }
    }
}