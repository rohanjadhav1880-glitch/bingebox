package com.bingebox.mediaplayer.model

import android.net.Uri

data class VideoItem(
    val id: Long,
    val title: String,
    val path: String,
    val uri: Uri,
    val durationMs: Long = 0L,
    val sizeBytes: Long = 0L,
    val resolution: String = "",
    val dateAdded: Long = 0L,
    val thumbnailUri: Uri? = null,
    val lastPositionMs: Long = 0L
)
