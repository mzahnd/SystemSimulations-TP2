package ar.edu.itba.ss

import java.io.File
import kotlin.random.Random

data class Settings(
    val probability: Double,
    val gridSize: Int,
    val gridSizeSquared: Int,
    val steps: Int,
    val random: Random,
    val outputFile: File
)
