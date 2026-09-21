package com.bingebox.mediaplayer.ui.components

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun PlayerControls(
    visible: Boolean,
    title: String,
    isPlaying: Boolean,
    currentPositionMs: Long,
    durationMs: Long,
    speed: Double = 1.0,
    aspectRatioName: String = "Fit",
    abStartMs: Long? = null,
    abEndMs: Long? = null,
    isLocked: Boolean = false,
    onPlayPauseToggle: () -> Unit,
    onSeek: (Long) -> Unit,
    onSeekRelative: (Int) -> Unit = {},
    onBackClick: () -> Unit,
    onSpeedCycle: () -> Unit = {},
    onAspectRatioCycle: () -> Unit = {},
    onEqualizerClick: () -> Unit,
    onSubtitlesClick: () -> Unit,
    onAbLoopClick: () -> Unit,
    onLockToggle: () -> Unit = {},
    onPipClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    // If locked, only show unlock button when visible
    if (isLocked) {
        AnimatedVisibility(
            visible = visible,
            enter = fadeIn(),
            exit = fadeOut(),
            modifier = modifier.fillMaxSize()
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(24.dp),
                contentAlignment = Alignment.TopStart
            ) {
                IconButton(
                    onClick = onLockToggle,
                    modifier = Modifier
                        .size(48.dp)
                        .background(Color(0x88000000), CircleShape)
                        .border(1.dp, Color(0xFF8B5CF6), CircleShape)
                ) {
                    Icon(
                        Icons.Default.Lock,
                        contentDescription = "Unlock Controls",
                        tint = Color(0xFF8B5CF6),
                        modifier = Modifier.size(24.dp)
                    )
                }
            }
        }
        return
    }

    var isScrubbing by remember { mutableStateOf(false) }
    var scrubPosMs by remember { mutableStateOf(0L) }

    val displayPosMs = if (isScrubbing) scrubPosMs else currentPositionMs

    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(),
        exit = fadeOut(),
        modifier = modifier.fillMaxSize()
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            // Top gradient scrim
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(140.dp)
                    .align(Alignment.TopCenter)
                    .background(
                        Brush.verticalGradient(
                            listOf(
                                Color(0xE00B0E14),
                                Color(0x800B0E14),
                                Color.Transparent
                            )
                        )
                    )
            )

            // Bottom gradient scrim
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(170.dp)
                    .align(Alignment.BottomCenter)
                    .background(
                        Brush.verticalGradient(
                            listOf(
                                Color.Transparent,
                                Color(0x990B0E14),
                                Color(0xF50B0E14)
                            )
                        )
                    )
            )

            // Main Controls Layout
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .statusBarsPadding()
                    .navigationBarsPadding()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                // Top Header Bar
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    IconButton(
                        onClick = onBackClick,
                        modifier = Modifier
                            .size(40.dp)
                            .background(Color(0x55000000), CircleShape)
                    ) {
                        Icon(
                            Icons.Default.ArrowBack,
                            contentDescription = "Back",
                            tint = Color.White,
                            modifier = Modifier.size(22.dp)
                        )
                    }

                    Column(
                        modifier = Modifier
                            .weight(1f)
                            .padding(horizontal = 12.dp)
                    ) {
                        Text(
                            text = title,
                            color = Color.White,
                            fontSize = 15.sp,
                            fontWeight = FontWeight.SemiBold,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        Text(
                            text = "BingeBox • 4K Hardware Accelerated",
                            color = Color(0xFFA78BFA),
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Normal
                        )
                    }

                    // Top Action Icons
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Aspect Ratio button
                        TextButton(
                            onClick = onAspectRatioCycle,
                            modifier = Modifier
                                .height(34.dp)
                                .background(Color(0x44FFFFFF), RoundedCornerShape(17.dp)),
                            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 0.dp)
                        ) {
                            Icon(
                                Icons.Default.AspectRatio,
                                contentDescription = "Aspect Ratio",
                                tint = Color.White,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(Modifier.width(4.dp))
                            Text(
                                text = aspectRatioName,
                                color = Color.White,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        // Speed button
                        TextButton(
                            onClick = onSpeedCycle,
                            modifier = Modifier
                                .height(34.dp)
                                .background(Color(0x44FFFFFF), RoundedCornerShape(17.dp)),
                            contentPadding = PaddingValues(horizontal = 8.dp, vertical = 0.dp)
                        ) {
                            Icon(
                                Icons.Default.Speed,
                                contentDescription = "Speed",
                                tint = Color.White,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(Modifier.width(2.dp))
                            Text(
                                text = "${speed}x",
                                color = Color.White,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        // Equalizer button
                        IconButton(
                            onClick = onEqualizerClick,
                            modifier = Modifier
                                .size(36.dp)
                                .background(Color(0x44FFFFFF), CircleShape)
                        ) {
                            Icon(
                                Icons.Default.GraphicEq,
                                contentDescription = "Equalizer",
                                tint = Color.White,
                                modifier = Modifier.size(18.dp)
                            )
                        }

                        // Subtitles button
                        IconButton(
                            onClick = onSubtitlesClick,
                            modifier = Modifier
                                .size(36.dp)
                                .background(Color(0x44FFFFFF), CircleShape)
                        ) {
                            Icon(
                                Icons.Default.Subtitles,
                                contentDescription = "Subtitles",
                                tint = Color.White,
                                modifier = Modifier.size(18.dp)
                            )
                        }

                        // PiP button
                        IconButton(
                            onClick = onPipClick,
                            modifier = Modifier
                                .size(36.dp)
                                .background(Color(0x44FFFFFF), CircleShape)
                        ) {
                            Icon(
                                Icons.Default.PictureInPictureAlt,
                                contentDescription = "PiP",
                                tint = Color.White,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                    }
                }

                // Center Playback Action Row
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 16.dp),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Rewind -10s
                    IconButton(
                        onClick = { onSeekRelative(-10) },
                        modifier = Modifier
                            .size(52.dp)
                            .background(Color(0x4D000000), CircleShape)
                            .border(1.dp, Color(0x33FFFFFF), CircleShape)
                    ) {
                        Icon(
                            Icons.Default.Replay10,
                            contentDescription = "Rewind 10s",
                            tint = Color.White,
                            modifier = Modifier.size(30.dp)
                        )
                    }

                    Spacer(Modifier.width(36.dp))

                    // Big Glowing Play / Pause Button
                    Box(
                        modifier = Modifier
                            .size(68.dp)
                            .shadow(16.dp, CircleShape, spotColor = Color(0xFF8B5CF6))
                            .background(
                                Brush.linearGradient(
                                    listOf(Color(0xFF8B5CF6), Color(0xFF7C3AED))
                                ),
                                CircleShape
                            )
                            .clickable(onClick = onPlayPauseToggle),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            if (isPlaying) Icons.Default.Pause else Icons.Default.PlayArrow,
                            contentDescription = if (isPlaying) "Pause" else "Play",
                            tint = Color.White,
                            modifier = Modifier.size(40.dp)
                        )
                    }

                    Spacer(Modifier.width(36.dp))

                    // Forward +10s
                    IconButton(
                        onClick = { onSeekRelative(10) },
                        modifier = Modifier
                            .size(52.dp)
                            .background(Color(0x4D000000), CircleShape)
                            .border(1.dp, Color(0x33FFFFFF), CircleShape)
                    ) {
                        Icon(
                            Icons.Default.Forward10,
                            contentDescription = "Forward 10s",
                            tint = Color.White,
                            modifier = Modifier.size(30.dp)
                        )
                    }
                }

                // Bottom Bar Controls
                Column(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    // Time and Progress Bar
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = formatTime(displayPosMs),
                            color = Color.White,
                            fontSize = 12.sp,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Medium
                        )

                        Slider(
                            value = if (durationMs > 0) {
                                (displayPosMs.toFloat() / durationMs.toFloat()).coerceIn(0f, 1f)
                            } else 0f,
                            onValueChange = { percent ->
                                isScrubbing = true
                                scrubPosMs = (percent * durationMs).toLong()
                            },
                            onValueChangeFinished = {
                                onSeek(scrubPosMs)
                                isScrubbing = false
                            },
                            modifier = Modifier
                                .weight(1f)
                                .padding(horizontal = 8.dp),
                            colors = SliderDefaults.colors(
                                thumbColor = Color(0xFF8B5CF6),
                                activeTrackColor = Color(0xFF8B5CF6),
                                inactiveTrackColor = Color(0x44FFFFFF)
                            )
                        )

                        Text(
                            text = formatTime(durationMs),
                            color = Color(0xFFCCCCCC),
                            fontSize = 12.sp,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Medium
                        )
                    }

                    // Bottom Secondary Row (A-B Repeat & Lock Button)
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 2.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // A-B Repeat Chip
                        Surface(
                            shape = RoundedCornerShape(14.dp),
                            color = if (abStartMs != null) Color(0x448B5CF6) else Color(0x22FFFFFF),
                            border = if (abStartMs != null) androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF8B5CF6)) else null,
                            modifier = Modifier.clickable(onClick = onAbLoopClick)
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    Icons.Default.Repeat,
                                    contentDescription = "A-B Repeat",
                                    tint = if (abStartMs != null) Color(0xFFA78BFA) else Color(0xFFB0B0B0),
                                    modifier = Modifier.size(16.dp)
                                )
                                Spacer(Modifier.width(6.dp))
                                Text(
                                    text = when {
                                        abStartMs != null && abEndMs != null -> "Loop: ${formatTime(abStartMs)} - ${formatTime(abEndMs)}"
                                        abStartMs != null -> "Loop A: ${formatTime(abStartMs)} (Tap to set B)"
                                        else -> "A-B Loop"
                                    },
                                    color = if (abStartMs != null) Color.White else Color(0xFFCCCCCC),
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }

                        // Lock Screen Button
                        IconButton(
                            onClick = onLockToggle,
                            modifier = Modifier
                                .size(32.dp)
                                .background(Color(0x22FFFFFF), CircleShape)
                        ) {
                            Icon(
                                Icons.Default.LockOpen,
                                contentDescription = "Lock Screen",
                                tint = Color(0xFFB0B0B0),
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}

private fun formatTime(ms: Long): String {
    if (ms <= 0) return "00:00"
    val totalSec = ms / 1000
    val sec = totalSec % 60
    val min = (totalSec / 60) % 60
    val hrs = totalSec / 3600
    return if (hrs > 0) {
        String.format("%02d:%02d:%02d", hrs, min, sec)
    } else {
        String.format("%02d:%02d", min, sec)
    }
}
