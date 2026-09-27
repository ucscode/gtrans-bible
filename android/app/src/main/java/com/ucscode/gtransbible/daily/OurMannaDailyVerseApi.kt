package com.ucscode.gtransbible.daily

import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

class OurMannaDailyVerseApi : DailyVerseApi {
    override fun fetchDailyVerse(): ApiDailyVerse {
        val connection = URL(ENDPOINT).openConnection() as HttpURLConnection
        try {
            connection.requestMethod = "GET"
            connection.connectTimeout = TIMEOUT_MILLIS
            connection.readTimeout = TIMEOUT_MILLIS
            connection.instanceFollowRedirects = true
            connection.useCaches = true
            connection.setRequestProperty("Accept", "application/json")
            if (connection.responseCode !in 200..299) {
                throw IOException("OurManna returned HTTP ${connection.responseCode}")
            }
            val body = connection.inputStream.use { input ->
                val output = ByteArrayOutputStream()
                val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
                var total = 0
                while (true) {
                    val count = input.read(buffer)
                    if (count < 0) break
                    total += count
                    if (total > MAX_RESPONSE_BYTES) throw IOException("OurManna response exceeded the size limit")
                    output.write(buffer, 0, count)
                }
                output.toString(Charsets.UTF_8.name())
            }
            return parseResponse(body)
        } finally {
            connection.disconnect()
        }
    }

    companion object {
        const val ENDPOINT = "https://beta.ourmanna.com/api/v1/get?format=json&order=daily"
        private const val TIMEOUT_MILLIS = 6_000
        private const val MAX_RESPONSE_BYTES = 64 * 1024

        fun parseResponse(json: String): ApiDailyVerse {
            val details = JSONObject(json).getJSONObject("verse").getJSONObject("details")
            val reference = details.optString("reference").trim()
            require(reference.isNotEmpty()) { "OurManna response has no verse reference" }
            val version = details.optString("version").trim().takeIf { it.isNotEmpty() }
            return ApiDailyVerse(reference, version?.let { "ourmanna:$it" } ?: "ourmanna")
        }
    }
}
