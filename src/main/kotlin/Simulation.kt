package ar.edu.itba.ss

import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.yield
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

private fun simulationStep(grid: Grid, settings: Settings): Grid {
    // N^2 updates
    repeat(settings.gridSizeSquared) {
        val column = settings.random.nextInt(settings.gridSize)
        val row = settings.random.nextInt(settings.gridSize)
        val newVote = metropolis(column, row, grid, settings)

        grid.set(column, row, newVote)
    }

    return grid
}

private fun calculateMagnetization(monteCarloStep: Grid, settings: Settings): Double =
    abs(monteCarloStep.sum().toDouble() / settings.gridSizeSquared)

private suspend fun writeOutputToFile(
    step: Int,
    magnetization: Double,
    grid: Grid,
    settings: Settings,
    dispatcher: CoroutineDispatcher = Dispatchers.IO
) = withContext(dispatcher) {
    val votes = StringBuilder()
    grid.forEachRaw { vote -> votes.append(",$vote") }
    settings.outputFile.appendText("$step,$magnetization,$votes\n")
}

suspend fun runSimulation(settings: Settings, dispatcher: CoroutineDispatcher = Dispatchers.Default) =
    withContext(dispatcher) {
        val grid = Grid(settings)
        for (step in 0 until settings.steps) {
            // N^2 updates
            simulationStep(grid, settings)
            // Calculate magnetization
            val magnetization = calculateMagnetization(grid, settings)

            yield()
            // Append in file
            writeOutputToFile(step, magnetization, grid, settings)
        }
    }