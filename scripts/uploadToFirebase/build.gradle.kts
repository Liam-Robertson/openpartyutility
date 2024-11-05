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
    mainClass.set("com.openparty.scripts.uploadDataToFirebase.MainKt")
}

// Run this using: ./gradlew :scripts:uploadDataToFirebase:run
