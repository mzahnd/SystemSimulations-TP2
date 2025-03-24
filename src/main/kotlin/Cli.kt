package ar.edu.itba.ss

import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.options.*
import com.github.ajalt.clikt.parameters.types.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import kotlin.random.Random

class Cli : CliktCommand() {
    private val logger = KotlinLogging.logger {}

    private val gridSize: Int by option("-n", "--grid-size").int().required()
        .help("Size of one side of the squared grid used by algorithm.")
        .check("Value must be greater than 0.") { it > 0 }
    private val probabilities: List<Double> by option("-p", "--probability").double()
        .multiple(required = true)
        .help("Probability that an individual changes its state. Giving more than one value (separating each by a comma ',') will run the algorithm once for each probability.")
        .check("All probabilities must be in range [0; 1].") { probabilities -> probabilities.isNotEmpty() && probabilities.all { it in 0.0..1.0 } }
    private val steps: List<Int> by option("-s", "--steps").int().multiple(required = true)
        .help("Monte Carlo steps to perform. Giving more than one value (separating each by a comma ',') will run the algorithm that many times, with that amount of steps each time.")
        .check("At least one step should be performed") { steps -> steps.isNotEmpty() && steps.all { it > 0 } }

    private val seed: Long by option().long().default(System.currentTimeMillis())
        .help("[Optional] Seed for the RND")
        .check("Seed must be greater or equal to 0.") { it > 0 }

    private val outputDirectory: Path by option().path(
        canBeFile = false,
        canBeDir = true,
        mustExist = true,
        mustBeReadable = true,
        mustBeWritable = true
    ).required().help("Path to the output directory.")

    override fun run() {
        logger.debug { "gridSize = ${gridSize}x${gridSize} " }
        logger.debug { "probability = $probabilities" }
        logger.debug { "steps = $steps" }
        logger.debug { "seed = $seed" }

        for (probability in probabilities) {
            for (step in steps) {
                val fileName = "n-${gridSize}_s-${step}_p-${probability}_seed-${seed}.csv"

                val settings = Settings(
                    probability = probability,
                    gridSize = gridSize,
                    gridSizeSquared = gridSize * gridSize,
                    steps = step,
                    random = Random(seed),
                    outputFile = outputDirectory.resolve(fileName).toFile()
                )
                logger.debug { "settings = $settings" }

                runSimulation(settings)
            }
        }
    }
}
