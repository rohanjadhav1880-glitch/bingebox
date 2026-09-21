package com.bingebox.mediaplayer.ui.components

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog

@Composable
fun AboutDialog(
    onDismiss: () -> Unit
) {
    val context = LocalContext.current

    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(24.dp),
            color = Color(0xFF10141E),
            border = BorderStroke(
                1.dp,
                Brush.verticalGradient(
                    listOf(Color(0xFF8B5CF6).copy(alpha = 0.6f), Color(0xFF1E2433))
                )
            ),
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp)
                    .verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Header with App Icon and Close button
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Spacer(Modifier.size(32.dp))

                    // Glowing App Icon
                    Box(
                        modifier = Modifier
                            .size(60.dp)
                            .background(
                                Brush.linearGradient(
                                    listOf(Color(0xFF8B5CF6), Color(0xFFEC4899))
                                ),
                                RoundedCornerShape(16.dp)
                            )
                            .border(
                                1.dp,
                                Color.White.copy(alpha = 0.25f),
                                RoundedCornerShape(16.dp)
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            Icons.Default.PlayArrow,
                            contentDescription = "BingeBox",
                            tint = Color.White,
                            modifier = Modifier.size(36.dp)
                        )
                    }

                    // Close Button
                    IconButton(
                        onClick = onDismiss,
                        modifier = Modifier
                            .size(32.dp)
                            .background(Color(0x22FFFFFF), CircleShape)
                    ) {
                        Icon(
                            Icons.Default.Close,
                            contentDescription = "Close",
                            tint = Color(0xFF94A3B8),
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }

                Spacer(Modifier.height(14.dp))

                // Title & Version
                Text(
                    text = "BingeBox",
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Black,
                    color = Color.White,
                    letterSpacing = 1.sp
                )

                Spacer(Modifier.height(4.dp))

                Surface(
                    shape = RoundedCornerShape(6.dp),
                    color = Color(0xFF8B5CF6).copy(alpha = 0.2f),
                    border = BorderStroke(1.dp, Color(0xFF8B5CF6).copy(alpha = 0.5f))
                ) {
                    Text(
                        text = "v1.1.0 • Android Mobile",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFFA78BFA),
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 3.dp)
                    )
                }

                Spacer(Modifier.height(10.dp))

                Text(
                    text = "High-performance, 100% standalone, 100% offline media player powered by native libmpv & FFmpeg.",
                    fontSize = 12.sp,
                    color = Color(0xFF94A3B8),
                    textAlign = TextAlign.Center,
                    lineHeight = 17.sp,
                    modifier = Modifier.padding(horizontal = 8.dp)
                )

                Spacer(Modifier.height(18.dp))

                // Feature Highlights
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color(0xFF161B28), RoundedCornerShape(14.dp))
                        .border(1.dp, Color(0xFF242C3E), RoundedCornerShape(14.dp))
                        .padding(14.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    AboutFeatureRow(
                        icon = Icons.Default.Bolt,
                        title = "Hardware Accelerated",
                        desc = "Direct GPU MediaCodec decoding via libmpv"
                    )
                    AboutFeatureRow(
                        icon = Icons.Default.GraphicEq,
                        title = "Audio Enhancer & EQ",
                        desc = "Multi-preset equalizer, Night Mode & sync delay"
                    )
                    AboutFeatureRow(
                        icon = Icons.Default.Subtitles,
                        title = "Subtitles Engine",
                        desc = "Hardware-rendered SRT, ASS & VTT styling"
                    )
                    AboutFeatureRow(
                        icon = Icons.Default.Repeat,
                        title = "A-B Looper & Speed",
                        desc = "Native segment looping & 0.25x to 2.0x playback"
                    )
                    AboutFeatureRow(
                        icon = Icons.Default.Security,
                        title = "100% Private & Offline",
                        desc = "Zero telemetry, zero ads, zero external calls"
                    )
                }

                Spacer(Modifier.height(16.dp))

                // Credits & License
                Text(
                    text = "Created with ❤️ by CAPTAIN NEMO",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFFE2E8F0)
                )
                Text(
                    text = "Released under the MIT License",
                    fontSize = 11.sp,
                    color = Color(0xFF64748B)
                )

                Spacer(Modifier.height(16.dp))

                // Action Links
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    OutlinedButton(
                        onClick = {
                            val intent = Intent(
                                Intent.ACTION_VIEW,
                                Uri.parse("https://github.com/rohanjadhav1880-glitch/bingebox")
                            )
                            context.startActivity(intent)
                        },
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(12.dp),
                        border = BorderStroke(1.dp, Color(0xFF334155)),
                        colors = ButtonDefaults.outlinedButtonColors(
                            containerColor = Color(0xFF161B28)
                        ),
                        contentPadding = PaddingValues(vertical = 10.dp)
                    ) {
                        Icon(
                            Icons.Default.Code,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(Modifier.width(6.dp))
                        Text(
                            "GitHub",
                            color = Color.White,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }

                    Button(
                        onClick = {
                            val intent = Intent(
                                Intent.ACTION_VIEW,
                                Uri.parse("https://buymeacoffee.com/nemo7299")
                            )
                            context.startActivity(intent)
                        },
                        modifier = Modifier.weight(1.2f),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFFFF813F)
                        ),
                        contentPadding = PaddingValues(vertical = 10.dp)
                    ) {
                        Icon(
                            Icons.Default.Coffee,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(Modifier.width(6.dp))
                        Text(
                            "Buy Coffee",
                            color = Color.White,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun AboutFeatureRow(
    icon: ImageVector,
    title: String,
    desc: String
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier.fillMaxWidth()
    ) {
        Box(
            modifier = Modifier
                .size(32.dp)
                .background(Color(0xFF8B5CF6).copy(alpha = 0.15f), CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                icon,
                contentDescription = null,
                tint = Color(0xFFA78BFA),
                modifier = Modifier.size(16.dp)
            )
        }
        Spacer(Modifier.width(10.dp))
        Column {
            Text(
                text = title,
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
                color = Color.White
            )
            Text(
                text = desc,
                fontSize = 10.sp,
                color = Color(0xFF94A3B8)
            )
        }
    }
}
