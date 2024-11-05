// build.gradle.kts (project level)
plugins {
    kotlin("jvm") version "1.8.0" apply false
}

allprojects {
    repositories {
        mavenCentral()
    }
}

subprojects {
    apply(plugin = "org.jetbrains.kotlin.jvm")
    apply(plugin = "application")

    repositories {
        mavenCentral()
    }
}
