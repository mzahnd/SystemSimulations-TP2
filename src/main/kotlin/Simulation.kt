package ar.edu.itba.ss

import io.github.oshai.kotlinlogging.KotlinLogging
import kotlin.math.abs

private val logger = KotlinLogging.logger {}

private fun metropolis(column: Int, row: Int, grid: Grid, settings: Settings): Vote {
    val p = settings.random.nextDouble()
    val originalVote = grid.get(column, row)

    return if (p < settings.probability) {
        // With probability p change the current state
        originalVote.switchVote()
    } else {
        // With probability (1-p) adopt the vote of the majority
        val votesSum = grid.getNeighbors(column, row).sumOf { it.value }
        val majorityVote = when {
            votesSum > 0 -> Vote.RIGHT_WING
            votesSum < 0 -> Vote.LEFT_WING
            else -> originalVote
        }

        majorityVote
    }
}

private fun simulationStep(settings: Settings): Grid {
    val grid = Grid(settings)

    // N^2 updates
    repeat(settings.gridSizeSquared) {
        val column = settings.random.nextInt(settings.gridSize)
        val row = settings.random.nextInt(settings.gridSize)
        val newVote = metropolis(column, row, grid, settings)

        grid.set(column, row, newVote)
    }

    return grid
}

private fun calculateMagnetization(monteCarloStep: Grid, settings: Settings): Double {
    val sum = monteCarloStep.sum()
    logger.debug { "sum: $sum" }
    return abs(sum.toDouble() / settings.gridSizeSquared)
}


private fun writeOutputToFile(grid: Grid, magnetization: Double, settings: Settings) {
    settings.outputFile.appendText("$magnetization")
    grid.forEachRaw { vote ->
        settings.outputFile.appendText(",$vote")
    }
    settings.outputFile.appendText("\n")
}

fun runSimulation(settings: Settings) {
    repeat(settings.steps) {
        // N^2 updates
        val monteCarloStep = simulationStep(settings)
        // Calculate magnetization
        val magnetization = calculateMagnetization(monteCarloStep, settings)
        // Append in file
        writeOutputToFile(monteCarloStep, magnetization, settings)
    }
}