plugins {
    kotlin("jvm")
    application
}

repositories {
    mavenCentral()
}

dependencies {
    implementation(kotlin("stdlib"))
}

application {
    mainClass.set("com.openparty.scripts.readTextAndStoreAudio.MainKt")
}

// Run this using: ./gradlew :scripts:readTextAndStoreAudio:run
