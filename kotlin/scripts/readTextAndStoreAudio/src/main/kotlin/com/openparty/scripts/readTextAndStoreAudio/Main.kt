package com.openparty.scripts.readTextAndStoreAudio

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import java.io.File
import java.io.IOException
import okio.buffer
import okio.sink

fun main() {
    val baseDir = File(System.getProperty("user.dir"))
    val inputDir = File(baseDir, "inputTextFiles")
    val outputDir = File(baseDir, "outputAudioFiles")

    if (!inputDir.exists() || !inputDir.isDirectory) {
        println("Creating input directory at ${inputDir.absolutePath}")
        inputDir.mkdirs()
    }

    if (!outputDir.exists()) {
        println("Creating output directory at ${outputDir.absolutePath}")
        outputDir.mkdirs()
    }

    // Find all .txt files in the input directory
    val textFiles = inputDir.listFiles { file -> file.extension == "txt" }
    if (textFiles.isNullOrEmpty()) {
        println("No text files found in ${inputDir.absolutePath}")
        return
    }

    val apiKey = System.getenv("OPENAI_API_KEY")
    if (apiKey.isNullOrEmpty()) {
        println("Please set the OPENAI_API_KEY environment variable.")
        return
    }

    val client = OkHttpClient()
    val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
    val jsonAdapter = moshi.adapter(TTSRequest::class.java)

    textFiles.forEach { textFile ->
        val text = try {
            textFile.readText()
        } catch (e: IOException) {
            println("Error reading file ${textFile.name}: ${e.message}")
            return@forEach
        }

        val ttsRequest = TTSRequest(
            model = "tts-1",
            input = text,
            voice = "alloy",
            responseFormat = "mp3"
        )

        val requestBody = jsonAdapter.toJson(ttsRequest)
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url("https://api.openai.com/v1/audio/speech")
            .addHeader("Authorization", "Bearer $apiKey")
            .post(requestBody)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                println("Error: ${response.code} - ${response.message}")
                return@forEach
            }

            val responseBody = response.body
            if (responseBody == null) {
                println("Error: Response body is null for file ${textFile.name}")
                return@forEach
            }

            val outputFile = File(outputDir, "${textFile.nameWithoutExtension}.mp3")
            try {
                responseBody.byteStream().use { inputStream ->
                    outputFile.sink().buffer().use { outputStream ->
                        inputStream.copyTo(outputStream.outputStream())
                    }
                }
                println("Audio content written to file ${outputFile.absolutePath}")
            } catch (e: IOException) {
                println("Error writing audio file for ${textFile.name}: ${e.message}")
            }
        }
    }
}

data class TTSRequest(
    val model: String,
    val input: String,
    val voice: String,
    val responseFormat: String
)
