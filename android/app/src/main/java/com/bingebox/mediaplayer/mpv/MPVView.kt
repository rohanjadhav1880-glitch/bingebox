package com.bingebox.mediaplayer.mpv

import android.content.Context
import android.util.AttributeSet
import android.util.Log
import android.view.SurfaceHolder
import android.view.SurfaceView
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import `is`.xyz.mpv.MPVLib

object MPVPlayerManager {
    @Volatile
    var isSurfaceReady: Boolean = false
    @Volatile
    var pendingFile: String? = null

    fun play(path: String) {
        Log.d("MPVPlayerManager", "play requested: $path, surfaceReady: $isSurfaceReady")
        if (isSurfaceReady) {
            try {
                MPVLib.command(arrayOf("loadfile", path))
                MPVLib.setPropertyString("vo", "gpu")
                MPVLib.setPropertyString("vid", "auto")
                MPVLib.setPropertyBoolean("pause", false)
            } catch (e: Throwable) {
                Log.e("MPVPlayerManager", "Error in loadfile", e)
            }
        } else {
            pendingFile = path
        }
    }

    fun onSurfaceAttached() {
        Log.d("MPVPlayerManager", "onSurfaceAttached, pendingFile: $pendingFile")
        isSurfaceReady = true
        pendingFile?.let { path ->
            try {
                MPVLib.command(arrayOf("loadfile", path))
                MPVLib.setPropertyString("vo", "gpu")
                MPVLib.setPropertyString("vid", "auto")
                MPVLib.setPropertyBoolean("pause", false)
            } catch (e: Throwable) {
                Log.e("MPVPlayerManager", "Error loading pending file", e)
            }
            pendingFile = null
        }
    }

    fun onSurfaceDetached() {
        Log.d("MPVPlayerManager", "onSurfaceDetached")
        isSurfaceReady = false
    }

    fun stop() {
        Log.d("MPVPlayerManager", "stop requested")
        pendingFile = null
        try {
            MPVLib.command(arrayOf("stop"))
        } catch (e: Throwable) {
            Log.e("MPVPlayerManager", "Error in stop", e)
        }
    }
}

class MPVSurfaceView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : SurfaceView(context, attrs), SurfaceHolder.Callback {

    init {
        holder.addCallback(this)
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        try {
            Log.d("MPVSurfaceView", "surfaceCreated: attaching surface")
            MPVLib.attachSurface(holder.surface)
            MPVLib.setPropertyString("vo", "gpu")
            MPVLib.setPropertyString("vid", "auto")
            MPVPlayerManager.onSurfaceAttached()
        } catch (e: Throwable) {
            Log.e("MPVSurfaceView", "Error in surfaceCreated", e)
        }
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        try {
            Log.d("MPVSurfaceView", "surfaceChanged: ${width}x${height}")
            MPVLib.setPropertyString("android-surface-size", "${width}x$height")
        } catch (e: Throwable) {
            Log.e("MPVSurfaceView", "Error in surfaceChanged", e)
        }
    }

    override fun surfaceDestroyed(holder: SurfaceHolder) {
        try {
            Log.d("MPVSurfaceView", "surfaceDestroyed: detaching surface")
            MPVPlayerManager.onSurfaceDetached()
            MPVLib.setPropertyString("vo", "null")
            MPVLib.detachSurface()
        } catch (e: Throwable) {
            Log.e("MPVSurfaceView", "Error in surfaceDestroyed", e)
        }
    }
}

@Composable
fun MPVView(
    modifier: Modifier = Modifier
) {
    AndroidView(
        factory = { context ->
            MPVSurfaceView(context)
        },
        modifier = modifier
    )
}
