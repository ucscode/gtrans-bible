package com.ucscode.gtransbible.data

import android.content.Context
import androidx.core.content.edit
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.security.MessageDigest

class DatabaseInstaller(private val context: Context) {
    data class Result(val copiedFiles: List<String>, val hashes: Map<String, String>)

    fun install(): Result {
        val manifest = context.assets.open("database-manifest.json").bufferedReader().use { it.readText() }
        val entries = JSONObject(manifest).getJSONArray("databases")
        val directory = File(context.filesDir, "databases")
        if (!directory.exists() && !directory.mkdirs()) {
            error("Could not create private database directory: ${directory.absolutePath}")
        }

        val copied = mutableListOf<String>()
        val hashes = linkedMapOf<String, String>()
        val versions = linkedMapOf<String, String>()
        for (index in 0 until entries.length()) {
            val entry = entries.getJSONObject(index)
            val filename = entry.getString("filename")
            require(filename in REQUIRED_DATABASES) { "Unexpected bundled database: $filename" }
            val expectedHash = entry.getString("sha256")
            require(expectedHash.matches(Regex("[0-9a-f]{64}"))) { "Invalid database hash for $filename" }
            val target = File(directory, filename)
            hashes[filename] = expectedHash
            versions[filename] = listOf(
                entry.optString("edition_id", "unknown"),
                entry.optString("version", "unspecified"),
                entry.optString("normalization_version", "unspecified"),
            ).joinToString("/")
            if (target.isFile && sha256(target) == expectedHash) continue

            val temporary = File(directory, "$filename.installing")
            if (temporary.exists() && !temporary.delete()) error("Could not clear incomplete database copy: ${temporary.name}")
            try {
                context.assets.open("databases/$filename").use { input ->
                    FileOutputStream(temporary).use { output ->
                        input.copyTo(output)
                        output.fd.sync()
                    }
                }
                check(sha256(temporary) == expectedHash) { "Checksum verification failed for $filename" }
                if (!temporary.renameTo(target)) error("Could not atomically install $filename")
                target.setWritable(false, true)
                copied += filename
            } catch (failure: Exception) {
                temporary.delete()
                throw IllegalStateException("Could not install local Bible database $filename: ${failure.message}", failure)
            }
        }

        require(hashes.keys == REQUIRED_DATABASES) { "Debug bundle is missing one or more required Bible databases" }
        context.getSharedPreferences(PREFERENCES, Context.MODE_PRIVATE).edit {
            putInt("manifest_version", 1)
            putString("database_hashes", hashes.toSortedMap().entries.joinToString(";") { "${it.key}:${it.value}" })
            putString("edition_versions", versions.toSortedMap().entries.joinToString(";") { "${it.key}:${it.value}" })
        }
        return Result(copied, hashes)
    }

    private fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().buffered().use { input ->
            val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
            while (true) {
                val count = input.read(buffer)
                if (count < 0) break
                digest.update(buffer, 0, count)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    companion object {
        val REQUIRED_DATABASES = setOf("bible.sqlite", "igbob-modern.sqlite", "kjv.sqlite")
        private const val PREFERENCES = "local_database_install"
    }
}
