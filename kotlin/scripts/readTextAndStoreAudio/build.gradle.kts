plugins {
    kotlin("jvm")
    application
}

repositories {
    mavenCentral()
}

dependencies {
    implementation(kotlin("stdlib"))
    implementation("com.squareup.okhttp3:okhttp:4.9.3")
    implementation("com.squareup.moshi:moshi:1.12.0")
    implementation("com.squareup.moshi:moshi-kotlin:1.12.0")
}

application {
    mainClass.set("com.openparty.scripts.readTextAndStoreAudio.MainKt")
}

// Run this using: ./gradlew :scripts:readTextAndStoreAudio:run
