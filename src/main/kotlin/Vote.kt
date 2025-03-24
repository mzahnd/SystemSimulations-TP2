package ar.edu.itba.ss

enum class Vote(val value: Int) {
    LEFT_WING(-1),
    RIGHT_WING(1);


    fun switchVote(): Vote = if (this == LEFT_WING) RIGHT_WING else LEFT_WING

    companion object {
        private val map = entries.associateBy(Vote::value)
        fun fromInt(value: Int) = map[value]
    }
}

fun randomVote(settings: Settings): Vote =
    if (settings.random.nextInt(2) == 0) {
        Vote.LEFT_WING
    } else {
        Vote.RIGHT_WING
    }
