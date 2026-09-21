package com.bingebox.mediaplayer.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// BingeBox Theme Color Palettes
val ObsidianPrimary = Color(0xFFFF2A5F)
val ObsidianBackground = Color(0xFF0F0F12)
val ObsidianSurface = Color(0xFF18181F)
val ObsidianOnSurface = Color(0xFFFFFFFF)

val CyberpunkPrimary = Color(0xFF00F0FF)
val CyberpunkBackground = Color(0xFF0D0221)
val CyberpunkSurface = Color(0xFF261447)

val FrostPrimary = Color(0xFF3B82F6)
val FrostBackground = Color(0xFF0F172A)
val FrostSurface = Color(0xFF1E293B)

private val DarkColorScheme = darkColorScheme(
    primary = ObsidianPrimary,
    background = ObsidianBackground,
    surface = ObsidianSurface,
    onSurface = ObsidianOnSurface,
    surfaceVariant = Color(0xFF242430),
    secondary = Color(0xFFFF7597)
)

private val CyberpunkColorScheme = darkColorScheme(
    primary = CyberpunkPrimary,
    background = CyberpunkBackground,
    surface = CyberpunkSurface,
    onSurface = Color(0xFFFF007F),
    secondary = Color(0xFFFF007F)
)

enum class AppTheme {
    OBSIDIAN, CYBERPUNK, FROST, LIGHT
}

@Composable
fun BingeBoxTheme(
    appTheme: AppTheme = AppTheme.OBSIDIAN,
    content: @Composable () -> Unit
) {
    val colorScheme = when (appTheme) {
        AppTheme.CYBERPUNK -> CyberpunkColorScheme
        AppTheme.FROST -> darkColorScheme(primary = FrostPrimary, background = FrostBackground, surface = FrostSurface)
        else -> DarkColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
