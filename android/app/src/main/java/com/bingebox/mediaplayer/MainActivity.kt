package com.bingebox.mediaplayer

import android.Manifest
import android.app.PictureInPictureParams
import android.content.ContentUris
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.content.res.Configuration
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.provider.OpenableColumns
import android.util.Log
import android.util.Rational
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.ContextCompat
import com.bingebox.mediaplayer.model.VideoItem
import com.bingebox.mediaplayer.mpv.MPVPlayerManager
import com.bingebox.mediaplayer.mpv.MPVView
import com.bingebox.mediaplayer.ui.components.*
import com.bingebox.mediaplayer.ui.theme.BingeBoxTheme
import `is`.xyz.mpv.MPVLib
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import java.io.File

class MainActivity : ComponentActivity() {

    private var isInPipMode by mutableStateOf(false)
    private var externalVideoUri by mutableStateOf<Uri?>(null)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize libmpv native engine with full GPU context
        try {
            MPVLib.create(applicationContext)
            MPVLib.setupHardwareAcceleration()
            MPVLib.init()
        } catch (e: Throwable) {
            Log.e("BingeBox", "Failed to initialize MPVLib", e)
        }

        // Check if opened via intent
        intent?.data?.let { uri ->
            externalVideoUri = uri
        }

        setContent {
            BingeBoxTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = Color(0xFF0B0E14)
                ) {
                    MainAppContainer(
                        externalUri = externalVideoUri,
                        onExternalUriHandled = { externalVideoUri = null },
                        isInPip = isInPipMode,
                        onEnterPip = { enterPipMode() }
                    )
                }
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        intent.data?.let { uri ->
            externalVideoUri = uri
        }
    }

    private fun enterPipMode() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val params = PictureInPictureParams.Builder()
                .setAspectRatio(Rational(16, 9))
                .build()
            enterPictureInPictureMode(params)
        }
    }

    override fun onUserLeaveHint() {
        super.onUserLeaveHint()
        enterPipMode()
    }

    override fun onPictureInPictureModeChanged(
        isInPictureInPictureMode: Boolean,
        newConfig: Configuration
    ) {
        super.onPictureInPictureModeChanged(isInPictureInPictureMode, newConfig)
        isInPipMode = isInPictureInPictureMode
    }

    override fun onPause() {
        super.onPause()
        try {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.N || !isInPictureInPictureMode) {
                MPVLib.command(arrayOf("set", "pause", "yes"))
            }
        } catch (e: Throwable) {
            Log.e("BingeBox", "Error onPause pause command", e)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            MPVPlayerManager.stop()
            MPVLib.destroy()
        } catch (e: Throwable) {
            Log.e("BingeBox", "Error onDestroy", e)
        }
    }
}

@Composable
fun MainAppContainer(
    externalUri: Uri?,
    onExternalUriHandled: () -> Unit,
    isInPip: Boolean,
    onEnterPip: () -> Unit
) {
    val context = LocalContext.current
    var activeVideo by remember { mutableStateOf<VideoItem?>(null) }
    var isPlaying by remember { mutableStateOf(true) }
    var controlsVisible by remember { mutableStateOf(true) }
    var showEqualizer by remember { mutableStateOf(false) }
    var isLocked by remember { mutableStateOf(false) }

    var currentPosMs by remember { mutableStateOf(0L) }
    var durationMs by remember { mutableStateOf(0L) }

    var abStartMs by remember { mutableStateOf<Long?>(null) }
    var abEndMs by remember { mutableStateOf<Long?>(null) }

    val speeds = listOf(1.0, 1.25, 1.5, 2.0, 0.5)
    var currentSpeedIdx by remember { mutableStateOf(0) }

    val aspectRatios = listOf("Fit", "Fill", "16:9", "4:3")
    var currentAspectIdx by remember { mutableStateOf(0) }

    var eqPreset by remember { mutableStateOf("Flat") }
    var nightMode by remember { mutableStateOf(false) }
    var audioDelayMs by remember { mutableStateOf(0f) }

    var deviceVideos by remember { mutableStateOf<List<VideoItem>>(emptyList()) }
    var currentPlaylist by remember { mutableStateOf<List<VideoItem>>(emptyList()) }
    var currentVideoIndex by remember { mutableStateOf(-1) }
    var userInteractionCount by remember { mutableStateOf(0) }

    fun playVideoAtIndex(index: Int) {
        if (index in currentPlaylist.indices) {
            val video = currentPlaylist[index]
            currentVideoIndex = index
            activeVideo = video
            currentPosMs = 0L
            durationMs = 0L
            isPlaying = true
            controlsVisible = true
            abStartMs = null
            abEndMs = null
            MPVPlayerManager.play(video.path)
        }
    }

    fun refreshDeviceVideos() {
        try {
            deviceVideos = queryDeviceVideos(context)
        } catch (e: Throwable) {
            Log.e("BingeBox", "Failed to query videos", e)
        }
    }

    // Storage permission launcher for scanning device videos
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            refreshDeviceVideos()
        }
    }

    LaunchedEffect(Unit) {
        val permission = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            Manifest.permission.READ_MEDIA_VIDEO
        } else {
            Manifest.permission.READ_EXTERNAL_STORAGE
        }

        if (ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED) {
            refreshDeviceVideos()
        } else {
            permissionLauncher.launch(permission)
        }
    }

    // Open file picker launcher (works universally on all Android versions)
    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument()
    ) { uri: Uri? ->
        uri?.let {
            val video = resolveUriToVideoItem(context, it)
            currentPlaylist = listOf(video)
            currentVideoIndex = 0
            playVideoAtIndex(0)
        }
    }

    // Handle external video uri from intents
    LaunchedEffect(externalUri) {
        externalUri?.let { uri ->
            val video = resolveUriToVideoItem(context, uri)
            currentPlaylist = listOf(video)
            currentVideoIndex = 0
            playVideoAtIndex(0)
            onExternalUriHandled()
        }
    }

    // Real-time polling loop for position, duration and playback state
    LaunchedEffect(activeVideo) {
        if (activeVideo != null) {
            while (isActive) {
                try {
                    val pos = MPVLib.getPropertyDouble("time-pos") ?: -1.0
                    val dur = MPVLib.getPropertyDouble("duration") ?: 0.0
                    val paused = MPVLib.getPropertyBoolean("pause") ?: false

                    if (pos >= 0.0) {
                        currentPosMs = (pos * 1000).toLong()
                    }
                    if (dur > 0.0) {
                        durationMs = (dur * 1000).toLong()
                    }
                    isPlaying = !paused
                } catch (e: Throwable) {
                    // ignore polling errors
                }
                delay(200)
            }
        }
    }

    // Auto-hide controls after 3.5s of playing inactivity
    LaunchedEffect(controlsVisible, isPlaying, userInteractionCount, isLocked) {
        if (controlsVisible && isPlaying && !isLocked) {
            delay(3500)
            controlsVisible = false
        }
    }

    Box(modifier = Modifier.fillMaxSize().background(Color.Black)) {
        if (activeVideo != null) {
            GestureOverlay(
                isLocked = isLocked,
                onSingleTap = {
                    controlsVisible = !controlsVisible
                    userInteractionCount++
                },
                onDoubleTapSeek = { forward ->
                    val delta = if (forward) 10 else -10
                    MPVLib.command(arrayOf("seek", delta.toString(), "relative"))
                    userInteractionCount++
                }
            ) {
                MPVView(modifier = Modifier.fillMaxSize())

                if (!isInPip) {
                    PlayerControls(
                        visible = controlsVisible,
                        title = activeVideo?.title ?: "BingeBox",
                        isPlaying = isPlaying,
                        currentPositionMs = currentPosMs,
                        durationMs = durationMs,
                        speed = speeds[currentSpeedIdx],
                        aspectRatioName = aspectRatios[currentAspectIdx],
                        abStartMs = abStartMs,
                        abEndMs = abEndMs,
                        isLocked = isLocked,
                        hasPrevious = currentVideoIndex > 0 || currentPlaylist.size > 1,
                        hasNext = (currentVideoIndex in 0 until (currentPlaylist.size - 1)) || currentPlaylist.size > 1,
                        onPreviousClick = {
                            if (currentPosMs > 3000L) {
                                MPVLib.command(arrayOf("seek", "0", "absolute"))
                                currentPosMs = 0L
                            } else if (currentVideoIndex > 0) {
                                playVideoAtIndex(currentVideoIndex - 1)
                            } else if (currentPlaylist.size > 1) {
                                playVideoAtIndex(currentPlaylist.size - 1)
                            }
                            userInteractionCount++
                        },
                        onNextClick = {
                            if (currentVideoIndex in 0 until (currentPlaylist.size - 1)) {
                                playVideoAtIndex(currentVideoIndex + 1)
                            } else if (currentPlaylist.size > 1) {
                                playVideoAtIndex(0)
                            }
                            userInteractionCount++
                        },
                        onPlayPauseToggle = {
                            isPlaying = !isPlaying
                            MPVLib.command(arrayOf("cycle", "pause"))
                            userInteractionCount++
                        },
                        onSeek = { targetMs ->
                            currentPosMs = targetMs
                            MPVLib.command(arrayOf("seek", (targetMs / 1000.0).toString(), "absolute"))
                            userInteractionCount++
                        },
                        onSeekRelative = { deltaSec ->
                            MPVLib.command(arrayOf("seek", deltaSec.toString(), "relative"))
                            userInteractionCount++
                        },
                        onBackClick = {
                            MPVPlayerManager.stop()
                            activeVideo = null
                            currentVideoIndex = -1
                        },
                        onSpeedCycle = {
                            currentSpeedIdx = (currentSpeedIdx + 1) % speeds.size
                            val newSpeed = speeds[currentSpeedIdx]
                            MPVLib.setPropertyDouble("speed", newSpeed)
                            userInteractionCount++
                        },
                        onAspectRatioCycle = {
                            currentAspectIdx = (currentAspectIdx + 1) % aspectRatios.size
                            when (aspectRatios[currentAspectIdx]) {
                                "Fit" -> {
                                    MPVLib.setPropertyDouble("panscan", 0.0)
                                    MPVLib.setPropertyString("video-aspect-override", "-1")
                                }
                                "Fill" -> {
                                    MPVLib.setPropertyDouble("panscan", 1.0)
                                    MPVLib.setPropertyString("video-aspect-override", "-1")
                                }
                                "16:9" -> {
                                    MPVLib.setPropertyDouble("panscan", 0.0)
                                    MPVLib.setPropertyString("video-aspect-override", "16:9")
                                }
                                "4:3" -> {
                                    MPVLib.setPropertyDouble("panscan", 0.0)
                                    MPVLib.setPropertyString("video-aspect-override", "4:3")
                                }
                            }
                            userInteractionCount++
                        },
                        onEqualizerClick = {
                            showEqualizer = true
                            userInteractionCount++
                        },
                        onSubtitlesClick = {
                            MPVLib.command(arrayOf("cycle", "sub"))
                            userInteractionCount++
                        },
                        onAbLoopClick = {
                            if (abStartMs == null) {
                                abStartMs = currentPosMs
                            } else if (abEndMs == null) {
                                abEndMs = currentPosMs
                                MPVLib.command(arrayOf("set", "ab-loop-a", (abStartMs!! / 1000.0).toString()))
                                MPVLib.command(arrayOf("set", "ab-loop-b", (abEndMs!! / 1000.0).toString()))
                            } else {
                                abStartMs = null
                                abEndMs = null
                                MPVLib.command(arrayOf("set", "ab-loop-a", "no"))
                                MPVLib.command(arrayOf("set", "ab-loop-b", "no"))
                            }
                            userInteractionCount++
                        },
                        onLockToggle = {
                            isLocked = !isLocked
                            userInteractionCount++
                        },
                        onPipClick = onEnterPip
                    )
                }
            }
        } else {
            MediaLibraryScreen(
                videos = deviceVideos,
                onVideoSelect = { video ->
                    currentPlaylist = deviceVideos
                    val idx = deviceVideos.indexOfFirst { it.id == video.id }
                    playVideoAtIndex(if (idx >= 0) idx else 0)
                },
                onOpenFilePicker = { filePickerLauncher.launch(arrayOf("video/*")) }
            )
        }

        if (showEqualizer) {
            EqualizerSheet(
                onDismiss = { showEqualizer = false },
                selectedPreset = eqPreset,
                onPresetSelected = { preset ->
                    eqPreset = preset
                    when (preset) {
                        "Bass Boost" -> MPVLib.command(arrayOf("set", "af", "equalizer=f=60:width_type=o:width=1.5:g=8"))
                        "Vocal" -> MPVLib.command(arrayOf("set", "af", "equalizer=f=1000:width_type=o:width=2:g=5,equalizer=f=3000:width_type=o:width=2:g=4"))
                        "Pop" -> MPVLib.command(arrayOf("set", "af", "equalizer=f=120:width_type=o:width=1.5:g=4,equalizer=f=2000:width_type=o:width=2:g=3"))
                        "Rock" -> MPVLib.command(arrayOf("set", "af", "equalizer=f=100:width_type=o:width=1.5:g=5,equalizer=f=4000:width_type=o:width=2:g=4"))
                        else -> MPVLib.command(arrayOf("set", "af", ""))
                    }
                },
                nightModeEnabled = nightMode,
                onNightModeToggle = { enabled ->
                    nightMode = enabled
                    if (enabled) {
                        MPVLib.command(arrayOf("set", "af", "lavfi=[dynaudnorm=f=75:g=15:p=0.95]"))
                    } else {
                        MPVLib.command(arrayOf("set", "af", ""))
                    }
                },
                audioDelayMs = audioDelayMs,
                onAudioDelayChange = { delay ->
                    audioDelayMs = delay
                    MPVLib.setPropertyDouble("audio-delay", delay / 1000.0)
                }
            )
        }
    }
}

fun resolveUriToVideoItem(context: Context, uri: Uri): VideoItem {
    var displayName = uri.lastPathSegment ?: "Local Video"
    var durationMs = 0L
    var sizeBytes = 0L

    if (uri.scheme == "content") {
        try {
            val projection = arrayOf(
                OpenableColumns.DISPLAY_NAME,
                OpenableColumns.SIZE
            )
            context.contentResolver.query(uri, projection, null, null, null)?.use { cursor ->
                val nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                val sizeIndex = cursor.getColumnIndex(OpenableColumns.SIZE)
                if (cursor.moveToFirst()) {
                    if (nameIndex != -1) displayName = cursor.getString(nameIndex) ?: displayName
                    if (sizeIndex != -1) sizeBytes = cursor.getLong(sizeIndex)
                }
            }
        } catch (e: Exception) {
            Log.e("BingeBox", "Error querying content resolver", e)
        }
    }

    val mpvPath = if (uri.scheme == "content") {
        try {
            val pfd = context.contentResolver.openFileDescriptor(uri, "r")
            val fd = pfd?.detachFd() ?: -1
            if (fd != -1) "fdclose://$fd" else uri.toString()
        } catch (e: Exception) {
            uri.toString()
        }
    } else {
        uri.path ?: uri.toString()
    }

    return VideoItem(
        id = System.currentTimeMillis(),
        title = displayName,
        path = mpvPath,
        uri = uri,
        durationMs = durationMs,
        sizeBytes = sizeBytes
    )
}

fun queryDeviceVideos(context: Context): List<VideoItem> {
    val list = mutableListOf<VideoItem>()
    try {
        val projection = arrayOf(
            MediaStore.Video.Media._ID,
            MediaStore.Video.Media.DISPLAY_NAME,
            MediaStore.Video.Media.DURATION,
            MediaStore.Video.Media.SIZE,
            MediaStore.Video.Media.DATA
        )
        val sortOrder = "${MediaStore.Video.Media.DATE_ADDED} DESC"
        context.contentResolver.query(
            MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
            projection,
            null,
            null,
            sortOrder
        )?.use { cursor ->
            val idCol = cursor.getColumnIndexOrThrow(MediaStore.Video.Media._ID)
            val nameCol = cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DISPLAY_NAME)
            val durCol = cursor.getColumnIndexOrThrow(MediaStore.Video.Media.DURATION)
            val sizeCol = cursor.getColumnIndexOrThrow(MediaStore.Video.Media.SIZE)
            val dataCol = cursor.getColumnIndex(MediaStore.Video.Media.DATA)

            while (cursor.moveToNext()) {
                val id = cursor.getLong(idCol)
                val name = cursor.getString(nameCol) ?: "Video"
                val duration = cursor.getLong(durCol)
                val size = cursor.getLong(sizeCol)
                val contentUri = ContentUris.withAppendedId(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, id)
                val dataPath = if (dataCol != -1) cursor.getString(dataCol) else null
                val path = dataPath ?: contentUri.toString()

                list.add(
                    VideoItem(
                        id = id,
                        title = name,
                        path = path,
                        uri = contentUri,
                        durationMs = duration,
                        sizeBytes = size
                    )
                )
            }
        }
    } catch (e: Throwable) {
        Log.e("BingeBox", "Error querying MediaStore", e)
    }
    return list
}
